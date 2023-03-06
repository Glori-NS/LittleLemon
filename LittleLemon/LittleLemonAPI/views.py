from datetime import datetime

from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .helpers import IsManager, IsRestaurantStaff
from .models import Cart, Category, MenuItem, Order, OrderItem
from .serializers import (
    CartSerializer,
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
    UserSerializer,
)


@permission_classes([IsAuthenticated])
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["title", "price"]

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "POST":
            permission_classes = [IsManager]

        return [permission() for permission in permission_classes]


class MenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


@permission_classes([IsAdminUser])
class ManagersView(generics.ListCreateAPIView):
    queryset = Group.objects.get(name="Manager").user_set.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        if username := request.POST["username"]:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)

            return Response(status.HTTP_201_CREATED)

        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdminUser])
class RemoveManagerView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs["pk"])
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)

        return Response(status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class DeliveryCrewView(generics.ListCreateAPIView):
    queryset = Group.objects.get(name="Delivery crew").user_set.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        if username := request.POST["username"]:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Delivery crew")
            managers.user_set.add(user)

            return Response(status.HTTP_201_CREATED)

        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdminUser])
class RemoveDeliveryCrewView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs["pk"])
        managers = Group.objects.get(name="Delivery crew")
        managers.user_set.remove(user)

        return Response(status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.select_related("menuitem").filter(user=user)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        menu_item_id = self.request.data["menuitem"]
        quantity = self.request.data["quantity"]

        menu_item = MenuItem.objects.get(pk=menu_item_id)
        unit_price = menu_item.price
        price = unit_price * int(quantity)

        new_cart = Cart(
            user=user,
            menuitem=menu_item,
            quantity=quantity,
            unit_price=unit_price,
            price=price,
        )
        new_cart.save()
        return Response(CartSerializer(new_cart).data, status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        cart_items.delete()

        return Response(status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    ordering_fields = ["user", "status", "total"]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Manager").exists():
            return Order.objects.all()
        if user.groups.filter(name="Delivery crew").exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if (
            not user.groups.filter(name="Manager").exists()
            and not user.groups.filter(name="Delivery crew").exists()
        ):
            cart_items = Cart.objects.select_related("menuitem").filter(user=user)
            if not cart_items:
                return Response(status.HTTP_412_PRECONDITION_FAILED)

            total = sum([item.price for item in cart_items])
            order = Order(user=user, total=total, date=datetime.now())
            order.save()
            for item in cart_items:
                order_item = OrderItem(
                    order=order,
                    menuitem=item.menuitem,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    price=item.price,
                )
                order_item.save()
            cart_items.delete()
            return Response(status.HTTP_201_CREATED)

        return Response(status.HTTP_204_NO_CONTENT)


@permission_classes([IsAuthenticated])
class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if (
            user.groups.filter(name="Manager").exists()
            or user.groups.filter(name="Delivery crew").exists()
        ):
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_permissions(self):
        permission_classes = []
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = [IsRestaurantStaff]

        return [permission() for permission in permission_classes]

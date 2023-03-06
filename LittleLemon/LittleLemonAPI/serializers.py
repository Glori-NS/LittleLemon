from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Cart, Category, MenuItem, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
            "featured",
            "category",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        extra_kwargs = {"email": {"read_only": True}}


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id",
            "menuitem",
            "quantity",
            "unit_price",
            "price",
        ]
        extra_kwargs = {
            "quantity": {"min_value": 1},
            "unit_price": {"read_only": True},
            "price": {"read_only": True},
            "menuitem": {"label": "Menu Item"},
        }


class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order.id"
    )
    menuitem = MenuItemSerializer()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menuitem",
            "quantity",
            "unit_price",
            "price",
            "order_id",
        ]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "delivery_crew",
            "total",
            "date",
            "order_items",
        ]

        extra_kwargs = {
            "total": {"read_only": True},
            "date": {"read_only": True},
        }

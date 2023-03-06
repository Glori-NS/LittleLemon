from rest_framework.permissions import BasePermission


class IsRestaurantStaff(BasePermission):
    """
    Allows access only to delivery crew or managers.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and (
                request.user.is_staff
                or request.user.groups.filter(name="Manager").exists()
                or request.user.groups.filter(name="Delivery crew").exists()
            )
        )


class IsManager(BasePermission):
    """
    Allows access only to delivery crew or managers.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and (
                request.user.is_staff
                or request.user.groups.filter(name="Manager").exists()
            )
        )

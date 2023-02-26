from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class PermissionMixin(LoginRequiredMixin):
    """Allows to get and operate only user's data"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous and self.get_object().wallet != request.user.wallet:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class UserQueryset:
    """Queryset filtered by user"""
    @staticmethod
    def get_user_queryset(user, model):
        queryset = model.objects.filter(wallet=user.wallet)
        return queryset

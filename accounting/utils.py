from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin


class LoginRequiredMixinCustom(LoginRequiredMixin):
    """Redirect to login page if not authorized"""
    login_url = reverse_lazy('login')


class PermissionMixin(TemplateResponseMixin):
    """Allows to get and operate only user's data"""
    def render_to_response(self, context, **response_kwargs):
        if context.get('object').wallet_id == self.request.user.wallet.pk:
            return super(PermissionMixin, self).render_to_response(context, **response_kwargs)
        else:
            raise PermissionDenied()


class UserQueryset:
    """Queryset filtered by user"""
    def get_user_queryset(self, user, model):
        queryset = model.objects.filter(wallet=user.wallet)
        return queryset

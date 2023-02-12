from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin


class LoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')


class PermissionMixin(TemplateResponseMixin):
    def render_to_response(self, context, **response_kwargs):
        if context.get('object').wallet_id == self.request.user.wallet.pk:
            return super(PermissionMixin, self).render_to_response(context, **response_kwargs)
        else:
            raise PermissionDenied()


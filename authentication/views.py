from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from authentication.forms import *
from accounting.models import Wallet, Category, PaymentType


class Registry(CreateView):
    form_class = RegisterForm
    template_name = 'authentication/registry.html'
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        user = form.save()
        wallet = Wallet(owner=user)
        wallet.save()

        payment_type = PaymentType(wallet=wallet, name='Cash')
        payment_type.save()

        income_category = Category(name='Income', wallet=wallet, type='Income')
        income_category.save()

        expense_category = Category(name='Expense', wallet=wallet, type='Expense')
        expense_category.save()

        expense_category = Category(name='Transfer', wallet=wallet, type='Transfer', service=True)
        expense_category.save()

        login(self.request, user)

        return redirect('main')


class Login(LoginView):
    form_class = AuthenticationForm
    template_name = 'authentication/login.html'

    def get_success_url(self):
        return reverse_lazy('main')


def user_logout(request):
    logout(request)
    return redirect('main')

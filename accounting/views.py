from django.core.exceptions import PermissionDenied

from accounting.utils import LoginRequiredMixin, PermissionMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, TemplateView, UpdateView, DetailView

from accounting.filters import TransactionFilter
from accounting.forms import *
from accounting.models import Category, PaymentType, Transaction, Wallet


class Main(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = CreateTransactionForm
    template_name = 'accounting/main.html'
    success_url = reverse_lazy('main')
    extra_context = {}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_wallet = request.user.wallet
            transactions = Transaction.objects.filter(wallet=user_wallet).order_by('-date')[:5]
            for transaction in transactions:
                transaction.date = transaction.date.strftime('%d.%m')
                transaction.value = '%.2f' % transaction.value

            self.extra_context.update(
                {'transactions': transactions}
            )

        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = self.form_class(**self.get_form_kwargs())
        if self.request.user.is_authenticated:
            user_wallet = self.request.user.wallet
            form.fields['category'].queryset = form.fields['category'].queryset. \
                filter(wallet=user_wallet). \
                annotate(usage_count=Count('transaction__category')). \
                order_by('-usage_count')
            form.fields['payment_type'].queryset = form.fields['payment_type'].queryset. \
                filter(wallet=user_wallet). \
                annotate(usage_count=Count('transaction__payment_type')). \
                order_by('-usage_count')
        return form

    def form_valid(self, form):
        user_wallet = Wallet.objects.get(owner=self.request.user)
        form.instance.wallet = user_wallet
        if form.instance.category.type == 'Expense':
            form.instance.value = -abs(form.instance.value)
        response = super().form_valid(form)

        payment_type = form.instance.payment_type
        payment_type.balance += form.instance.value
        payment_type.save()

        return response


class Menu(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/menu.html'
    extra_context = {'menu': [{'title': 'Payment types', 'url_name': 'payment_types'},
                              {'title': 'Categories', 'url_name': 'categories'},
                              {'title': 'Transactions', 'url_name': 'transactions'}]}


class PaymentTypes(LoginRequiredMixin, ListView):
    model = PaymentType
    template_name = 'accounting/payment_types.html'
    context_object_name = 'payment_types'
    paginate_by = 5

    def get_queryset(self):
        current_user = self.request.user
        self.queryset = PaymentType.objects.filter(wallet=Wallet.objects.get(owner=current_user))
        queryset = super().get_queryset()

        for i in range(len(queryset)):
            queryset[i].balance = "{:,.2f}".format(float(self.queryset[i].balance)).replace(',', ' ')
        return queryset


class CreatePaymentType(LoginRequiredMixin, CreateView):
    model = PaymentType
    template_name = 'accounting/create_payment_type.html'
    form_class = CreatePaymentTypeForm
    success_url = reverse_lazy('payment_types')

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        form.instance.wallet = self.request.user.wallet
        return form


class UpdatePaymentType(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = PaymentType
    form_class = UpdatePaymentTypeForm
    template_name = 'accounting/update_payment_type.html'
    success_url = reverse_lazy('payment_types')


class DeletePaymentType(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = PaymentType
    template_name = 'accounting/delete_payment_type.html'
    success_url = reverse_lazy('payment_types')
    extra_context = {}

    def get(self, request, *args, **kwargs):
        user_wallet = Wallet.objects.get(owner=self.request.user)
        payment_type = self.get_object()
        form = DeletePaymentTypeForm()
        form.fields['name'].queryset = PaymentType.objects.filter(wallet=user_wallet).\
            exclude(pk=payment_type.pk).\
            annotate(usage_count=Count('transaction__payment_type')).order_by('-usage_count')

        self.extra_context.update({
            'form': form,
            'payment_type': payment_type
        })

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_wallet = request.user.wallet
        payment_type = self.get_object()
        payment_type_id = request.POST.get('name')
        payment_type_to_convey = PaymentType.objects.get(pk=payment_type_id)
        transactions = Transaction.objects.filter(wallet=user_wallet, payment_type=payment_type)
        for transaction in transactions:
            transaction.payment_type = payment_type_to_convey
            transaction.save()

        payment_type_to_convey.balance += payment_type.balance
        payment_type_to_convey.save()

        return super().post(request, *args, **kwargs)


class TransferBetweenPaymentTypes(LoginRequiredMixin, FormView):
    form_class = TransferBetweenPaymentTypesForm
    template_name = 'accounting/transfer_between_payment_types.html'
    success_url = reverse_lazy('payment_types')
    extra_context = {}

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        user_wallet = self.request.user.wallet
        form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        form.fields['payment_type_from'].queryset = PaymentType.objects.filter(wallet=user_wallet)
        form.fields['payment_type_to'].queryset = PaymentType.objects.filter(wallet=user_wallet)
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user_wallet = request.user.wallet
            data = form.cleaned_data
            payment_type_from = data['payment_type_from']
            payment_type_to = data['payment_type_to']
            value = data['value']
            description = data['description']

            if payment_type_to.wallet_id != user_wallet.id or payment_type_from.wallet_id != user_wallet.id:
                raise PermissionDenied()

            payment_type_from.balance -= value
            payment_type_from.save()

            payment_type_to.balance += value
            payment_type_to.save()

            transaction_from = Transaction(wallet=user_wallet, payment_type=payment_type_from,
                                           category=user_wallet.category_set.get(name='Transfer'), value=-value,
                                           description=f'Transfer from "{payment_type_from.name}" '
                                                       f'to "{payment_type_to.name}"\n{description}')
            transaction_from.save()
            transaction_to = Transaction(wallet=user_wallet, payment_type=payment_type_to,
                                         category=user_wallet.category_set.get(name='Transfer'), value=value,
                                         description=f'Transfer from "{payment_type_from.name}" '
                                                     f'to "{payment_type_to.name}"\n{description}')
            transaction_to.save()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class Categories(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'accounting/categories.html'
    context_object_name = 'categories'
    paginate_by = 5

    def get_queryset(self):
        current_user = self.request.user
        self.queryset = Category.objects.filter(wallet=Wallet.objects.get(owner=current_user), service=False)
        return super().get_queryset()


class CreateCategory(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'accounting/create_category.html'
    form_class = CreateCategoryForm
    success_url = reverse_lazy('categories')

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        form.instance.wallet = self.request.user.wallet
        return form


class UpdateCategory(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Category
    form_class = UpdateCategoryForm
    template_name = 'accounting/update_category.html'
    success_url = reverse_lazy('categories')


class DeleteCategory(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'accounting/delete_category.html'
    success_url = reverse_lazy('categories')
    extra_context = {}

    def get(self, request, *args, **kwargs):
        user_wallet = Wallet.objects.get(owner=self.request.user)
        current_object = self.get_object()
        form = DeleteCategoryForm()
        form.fields['new_category_name'].queryset = Category.objects.\
            filter(wallet=user_wallet, type=current_object.type).\
            exclude(pk=current_object.pk).\
            annotate(usage_count=Count('transaction__category')).order_by('-usage_count')

        self.extra_context.update({
            'form': form
        })

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_wallet = request.user.wallet
        category = self.get_object()
        category_type_id = request.POST.get('new_category_name')
        category_type_to_convey = Category.objects.get(pk=category_type_id)
        transactions = Transaction.objects.filter(wallet=user_wallet, category=category)
        for transaction in transactions:
            transaction.category = category_type_to_convey
            transaction.save()

        return super().post(request, *args, **kwargs)


class Transactions(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'accounting/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        user_wallet = self.request.user.wallet
        queryset = super().get_queryset()
        queryset = queryset.filter(wallet=user_wallet).order_by('-date')
        self.filtered_queryset = TransactionFilter(self.request.GET, queryset=queryset)
        for transaction in self.filtered_queryset.qs:
            transaction.date = transaction.date.strftime('%d.%m.%y')
        return self.filtered_queryset.qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        form = self.filtered_queryset.form
        user_wallet = self.request.user.wallet
        form.fields['category'].queryset = form.fields['category'].queryset. \
            filter(wallet=user_wallet). \
            annotate(usage_count=Count('transaction__category')). \
            order_by('-usage_count')
        form.fields['payment_type'].queryset = form.fields['payment_type'].queryset. \
            filter(wallet=user_wallet). \
            annotate(usage_count=Count('transaction__payment_type')). \
            order_by('-usage_count')

        income_sum = 0
        expense_sum = 0

        for transaction in self.filtered_queryset.qs:
            if transaction.category.type == 'Income':
                income_sum += transaction.value
            elif transaction.category.type == 'Expense':
                expense_sum += transaction.value

        income_all_time_sum = 0
        expense_all_time_sum = 0
        transactions = Transaction.objects.filter(wallet=user_wallet)
        for transaction in transactions:
            if transaction.category.type == 'Income':
                income_all_time_sum += transaction.value
            elif transaction.category.type == 'Expense':
                expense_all_time_sum += transaction.value

        context.update({
            'form': self.filtered_queryset.form,
            'income_sum': income_sum,
            'income_all_time_sum': income_all_time_sum,
            'expense_sum': expense_sum,
            'expense_all_time_sum': expense_all_time_sum
        })
        return context


class TransactionDetails(PermissionMixin, LoginRequiredMixin, DetailView):
    model = Transaction
    context_object_name = 'transaction'
    template_name = 'accounting/transaction_details.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['transaction'].date = context_data['transaction'].date.strftime('%d.%m.%Y %H:%M')
        return context_data


class UpdateTransaction(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = UpdateTransactionForm
    template_name = 'accounting/update_transaction.html'
    success_url = reverse_lazy('main')
    object = None

    def get_form(self, form_class=None):
        user_wallet = Wallet.objects.get(owner=self.request.user)
        form = self.form_class(**self.get_form_kwargs())
        form.fields['category'].queryset = Category.objects. \
            filter(wallet=user_wallet). \
            annotate(usage_count=Count('transaction__category')). \
            order_by('-usage_count')
        form.fields['payment_type'].queryset = form.fields['payment_type'].queryset. \
            filter(wallet=user_wallet). \
            annotate(usage_count=Count('transaction__payment_type')). \
            order_by('-usage_count')

        return form

    def form_valid(self, form):
        transaction = Transaction.objects.get(pk=self.object.pk)
        if self.object.category.type == 'Expense':
            self.object.value = -abs(self.object.value)
        old_value = transaction.value
        new_value = self.object.value

        transaction.payment_type.balance -= old_value
        transaction.payment_type.save()

        payment_type = PaymentType.objects.get(pk=self.object.payment_type.pk)
        payment_type.balance += new_value
        payment_type.save()

        return super().form_valid(form)

    def get_success_url(self):
        if self.request.GET.get('redirect_url'):
            return self.request.GET.get('redirect_url')
        else:
            return super().get_success_url()


class DeleteTransaction(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'accounting/delete_transaction.html'
    context_object_name = 'transaction'
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['transaction'].date = context_data['transaction'].date.strftime('%d.%m.%Y %H:%M')
        return context_data


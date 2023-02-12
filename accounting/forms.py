from django import forms
from django.core.exceptions import ValidationError

from accounting.models import PaymentType, Category, Transaction


class CreatePaymentTypeForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label='New name',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    balance = forms.DecimalField(max_digits=16, decimal_places=2,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                 initial=0)

    class Meta:
        model = PaymentType
        fields = ['name', 'balance']

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.Meta.model.objects.filter(wallet=self.instance.wallet, name__iexact=name).exists():
            raise ValidationError('A payment type with that name already exists.')
        return name


class UpdatePaymentTypeForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label='New name',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = PaymentType
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.Meta.model.objects.filter(wallet=self.instance.wallet, name__iexact=name).exists():
            raise ValidationError('A payment type with that name already exists.')
        return name


class DeletePaymentTypeForm(forms.Form):
    name = forms.ModelChoiceField(queryset=PaymentType.objects.all(),
                                  label='Select a new payment type for existing transactions',
                                  empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))


class CreateCategoryForm(forms.ModelForm):
    types = Category.transition_types
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(choices=types, initial=types[0][0], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Category
        fields = ['name', 'type']

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.Meta.model.objects.filter(wallet=self.instance.wallet, name__iexact=name).exists():
            raise ValidationError('A category with that name already exists.')
        return name


class UpdateCategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label='New name',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.Meta.model.objects.filter(wallet=self.instance.wallet, name__iexact=name).exists():
            raise ValidationError('A category with that name already exists.')
        return name


class DeleteCategoryForm(forms.Form):
    new_category_name = forms.ModelChoiceField(queryset=Category.objects.filter(service=False),
                                               label='Select a new category for existing transactions',
                                               empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))


class CreateTransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(service=False), empty_label=None,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    payment_type = forms.ModelChoiceField(queryset=PaymentType.objects.all(), empty_label=None,
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    value = forms.DecimalField(max_digits=16, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=255, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Transaction
        fields = ['payment_type', 'category', 'value', 'description']


class UpdateTransactionForm(CreateTransactionForm):
    date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local',
                                                                 'class': 'form-control',
                                                                 'max': '9999-12-31'}))

    class Meta:
        model = Transaction
        fields = ['payment_type', 'category', 'value', 'description', 'date']


class TransferBetweenPaymentTypesForm(forms.Form):
    payment_type_from = forms.ModelChoiceField(queryset=PaymentType.objects.all(), empty_label=None,
                                               widget=forms.Select(attrs={'class': 'form-control'}))
    payment_type_to = forms.ModelChoiceField(queryset=PaymentType.objects.all(), empty_label=None,
                                             widget=forms.Select(attrs={'class': 'form-control'}))
    value = forms.DecimalField(max_digits=16, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=255, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_payment_type_to(self):
        payment_type_from = self.cleaned_data['payment_type_from']
        payment_type_to = self.cleaned_data['payment_type_to']

        if payment_type_to == payment_type_from:
            raise ValidationError("You can't transfer between same payment types")

        return payment_type_to

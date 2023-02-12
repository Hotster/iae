import django_filters
from django import forms

from accounting.models import Transaction, PaymentType, Category


class TransactionFilter(django_filters.FilterSet):
    payment_type = django_filters.ModelMultipleChoiceFilter(queryset=PaymentType.objects.all(),
                                                            widget=forms.CheckboxSelectMultiple(
                                                                attrs={'class': 'form-checkbox'}))
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all(),
                                                        widget=forms.CheckboxSelectMultiple(
                                                            attrs={'class': 'form-checkbox'}))
    date = django_filters.DateFilter()
    date__gte = django_filters.DateFilter(field_name='date', lookup_expr='gte',
                                          widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control',
                                                                        'max': '9999-12-31',
                                                                        'placeholder': 'From'}))
    date__lte = django_filters.DateFilter(field_name='date', lookup_expr='lte',
                                          widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control',
                                                                        'max': '9999-12-31'}))
    value = django_filters.NumberFilter()
    value__gte = django_filters.NumberFilter(field_name='value', lookup_expr='gte',
                                             widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                             'placeholder': 'From'}))
    value__lte = django_filters.NumberFilter(field_name='value', lookup_expr='lte',
                                             widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                             'placeholder': 'To'}))
    description = django_filters.Filter(field_name='description', lookup_expr='icontains',
                                        label='Description',
                                        widget=forms.TextInput(attrs={'class': 'form-control',
                                                                      'placeholder': 'Description'}))

    class Meta:
        model = Transaction
        fields = []

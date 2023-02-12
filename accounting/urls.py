from django.urls import path

from accounting.views import *


urlpatterns = [
    path('', Main.as_view(), name='main'),
    path('menu/', Menu.as_view(), name='menu'),

    path('payment_types/', PaymentTypes.as_view(), name='payment_types'),
    path('payment_types/create/', CreatePaymentType.as_view(), name='create_payment_type'),
    path('payment_types/update/<int:pk>', UpdatePaymentType.as_view(), name='update_payment_type'),
    path('payment_types/delete/<int:pk>', DeletePaymentType.as_view(), name='delete_payment_type'),
    path('payment_types/transfer/', TransferBetweenPaymentTypes.as_view(), name='transfer_between_payment_types'),

    path('categories/', Categories.as_view(), name='categories'),
    path('categories/create_category/', CreateCategory.as_view(), name='create_category'),
    path('categories/update_category/<int:pk>', UpdateCategory.as_view(), name='update_category'),
    path('categories/delete_category/<int:pk>', DeleteCategory.as_view(), name='delete_category'),

    path('payment_types/', PaymentTypes.as_view(), name='incomes'),
    path('payment_types/', PaymentTypes.as_view(), name='expenses'),

    path('transactions/', Transactions.as_view(), name='transactions'),
    path('transactions/details/<int:pk>', TransactionDetails.as_view(), name='transaction_details'),
    path('transactions/update/<int:pk>', UpdateTransaction.as_view(), name='update_transaction'),
    path('transactions/delete/<int:pk>', DeleteTransaction.as_view(), name='delete_transaction')
]

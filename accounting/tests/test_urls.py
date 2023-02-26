from django.test import SimpleTestCase
from django.urls import reverse, resolve
from accounting.views import *


class TestUrls(SimpleTestCase):

    # Main
    def test_main_url_resolves(self):
        url = reverse('main')

        self.assertEqual(resolve(url).func.view_class, Main)

    # Payment types
    def test_payment_types_url_resolves(self):
        url = reverse('payment_types')

        self.assertEqual(resolve(url).func.view_class, PaymentTypes)

    def test_create_payment_type_url_resolves(self):
        url = reverse('create_payment_type')

        self.assertEqual(resolve(url).func.view_class, CreatePaymentType)

    def test_update_payment_type_url_resolves(self):
        url = reverse('update_payment_type', args=[1])

        self.assertEqual(resolve(url).func.view_class, UpdatePaymentType)

    def test_delete_payment_type_type_url_resolves(self):
        url = reverse('delete_payment_type', args=[1])

        self.assertEqual(resolve(url).func.view_class, DeletePaymentType)

    def test_transfer_between_payment_types_url_resolves(self):
        url = reverse('transfer_between_payment_types')

        self.assertEqual(resolve(url).func.view_class, TransferBetweenPaymentTypes)

    # Categories
    def test_categories_url_resolves(self):
        url = reverse('categories')

        self.assertEqual(resolve(url).func.view_class, Categories)

    def test_create_category_url_resolves(self):
        url = reverse('create_category')

        self.assertEqual(resolve(url).func.view_class, CreateCategory)

    def test_update_category_url_resolves(self):
        url = reverse('update_category', args=[1])

        self.assertEqual(resolve(url).func.view_class, UpdateCategory)

    def test_delete_category_url_resolves(self):
        url = reverse('delete_category', args=[1])

        self.assertEqual(resolve(url).func.view_class, DeleteCategory)

    # Transactions
    def test_transactions_url_resolves(self):
        url = reverse('transactions')

        self.assertEqual(resolve(url).func.view_class, Transactions)

    def test_transaction_details_url_resolves(self):
        url = reverse('transaction_details', args=[1])

        self.assertEqual(resolve(url).func.view_class, TransactionDetails)

    def test_update_transaction_url_resolves(self):
        url = reverse('update_transaction', args=[1])

        self.assertEqual(resolve(url).func.view_class, UpdateTransaction)

    def test_delete_transaction_url_resolves(self):
        url = reverse('delete_transaction', args=[1])

        self.assertEqual(resolve(url).func.view_class, DeleteTransaction)

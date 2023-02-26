import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounting.models import Wallet, PaymentType, Category, Transaction


class TestViewsUnauthorized(TestCase):
    """Unauthorized user. Expect redirecting to login page."""

    def setUp(self):
        self.client = Client()

    # Main
    def test_main_login_required(self):
        """Main page"""
        response = self.client.get(reverse('main'))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    # Payment types
    def test_payment_types_login_required(self):
        """Payment types"""
        response = self.client.get(reverse('payment_types'))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_create_payment_type_login_required(self):
        """Create a payment type"""
        response = self.client.get(reverse('create_payment_type'))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_update_payment_type_login_required(self):
        """Update a payment type"""
        response = self.client.get(reverse('update_payment_type', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_delete_payment_type_type_login_required(self):
        """Delete a payment type"""
        response = self.client.get(reverse('delete_payment_type', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_transfer_between_payment_types_login_required(self):
        """Transfer between payment types"""
        response = self.client.get(reverse('transfer_between_payment_types'))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    # Categories
    def test_categories_login_required(self):
        """Categories"""
        response = self.client.get(reverse('categories'))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_create_category_login_required(self):
        """Create a category"""
        response = self.client.get(reverse('create_category'))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_update_category_login_required(self):
        """Update a category"""
        response = self.client.get(reverse('update_category', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_delete_category_login_required(self):
        """Delete a payment type"""
        response = self.client.get(reverse('delete_category', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    # Transactions
    def test_transactions_login_required(self):
        """Transactions"""
        response = self.client.get(reverse('transactions'))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_transaction_details_login_required(self):
        """Transaction details"""
        response = self.client.get(reverse('transaction_details', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_update_transaction_login_required(self):
        """Update a transaction"""
        response = self.client.get(reverse('update_transaction', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))

    def test_delete_transaction_login_required(self):
        """Delete a transaction"""
        response = self.client.get(reverse('delete_transaction', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url.split('?')[0], reverse('login'))


class TestViews(TestCase):
    """Authorized user"""
    client = Client()
    client_username = 'testuser'
    client_password = '1234'

    client2 = Client()
    client2_username = 'testuser2'
    client2_password = '1234'

    user = None
    wallet = None
    payment_type = None
    income_category = None
    expense_category = None
    transfer_category = None

    user2 = None
    wallet2 = None
    payment_type2 = None
    income_category2 = None
    expense_category2 = None
    transfer_category2 = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username=cls.client_username, password=cls.client_password)
        cls.wallet = Wallet(owner=cls.user)
        cls.wallet.save()
        cls.payment_type = PaymentType(wallet=cls.wallet, name='Cash')
        cls.payment_type.save()
        cls.income_category = Category(name='Income', wallet=cls.wallet, type='Income')
        cls.income_category.save()
        cls.expense_category = Category(name='Expense', wallet=cls.wallet, type='Expense')
        cls.expense_category.save()
        cls.transfer_category = Category(name='Transfer', wallet=cls.wallet, type='Transfer', service=True)
        cls.transfer_category.save()

        cls.user2 = User.objects.create_user(username=cls.client2_username, password=cls.client2_password)
        cls.wallet2 = Wallet(owner=cls.user2)
        cls.wallet2.save()
        cls.payment_type2 = PaymentType(wallet=cls.wallet2, name='Cash')
        cls.payment_type2.save()
        cls.income_category2 = Category(name='Income', wallet=cls.wallet2, type='Income')
        cls.income_category2.save()
        cls.expense_category2 = Category(name='Expense', wallet=cls.wallet2, type='Expense')
        cls.expense_category2.save()
        cls.transfer_category2 = Category(name='Transfer', wallet=cls.wallet2, type='Transfer', service=True)
        cls.transfer_category2.save()

    def setUp(self):
        self.client.login(username=self.client_username, password=self.client_password)
        self.client2.login(username=self.client2_username, password=self.client2_password)

    # Main
    def test_main_GET(self):
        """Main page"""
        response = self.client.get(reverse('main'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/main.html')

    def test_main_GET_queryset(self):
        """Main page. Transaction queryset has only user data."""
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=self.payment_type,
                                                 category=self.income_category,
                                                 value=500)
        transaction2 = Transaction.objects.create(wallet=self.wallet2,
                                                  payment_type=self.payment_type2,
                                                  category=self.income_category2,
                                                  value=500)

        response = self.client.get(reverse('main'))

        self.assertEqual(self.user.wallet.transaction_set.all().count(),
                         len(response.context_data['transactions']))
        self.assertIn(transaction, response.context_data['transactions'])
        self.assertNotIn(transaction2, response.context_data['transactions'])

    def test_main_GET_form_select_fields(self):
        """Main page. Transaction form category and payment type fields
        have only user data"""
        response = self.client.get(reverse('main'))

        form_payment_types_qs = response.context_data['form'].fields['payment_type'].queryset
        form_categories_qs = response.context_data['form'].fields['category'].queryset

        self.assertEqual(len(form_payment_types_qs), self.user.wallet.paymenttype_set.all().count())
        self.assertEqual(len(form_categories_qs), self.user.wallet.category_set.all().count())
        for payment_type in form_payment_types_qs:
            self.assertEqual(self.user.wallet, payment_type.wallet)
        for category in form_categories_qs:
            self.assertEqual(self.user.wallet, category.wallet)

    def test_main_POST_add_new_transaction(self):
        """Main page. Transaction saves correctly."""
        description = 'New transaction'
        value = 500

        response = self.client.post(reverse('main'), data={
            'category': self.income_category.pk,
            'payment_type': self.payment_type.pk,
            'value': value,
            'description': description
        })
        self.payment_type.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.wallet.transaction_set.all().count(), 1)
        self.assertEqual(self.user.wallet.transaction_set.last().category, self.income_category)
        self.assertEqual(self.user.wallet.transaction_set.last().payment_type, self.payment_type)
        self.assertEqual(self.user.wallet.transaction_set.last().value, value)
        self.assertEqual(self.user.wallet.transaction_set.last().description, description)

    def test_main_POST_income_transaction_payment_type_balance(self):
        """Main page. After a successful income transaction
        it's payment type balance changes correctly."""
        description = 'Income transaction'
        value = 500
        self.payment_type.refresh_from_db()
        balance = self.payment_type.balance

        self.client.post(reverse('main'), data={
            'category': self.income_category.pk,
            'payment_type': self.payment_type.pk,
            'value': value,
            'description': description
        })
        self.payment_type.refresh_from_db()

        self.assertEqual(self.payment_type.balance, balance + value)

    def test_main_POST_expense_transaction_payment_type_balance(self):
        """Main page. After a successful expense transaction
        it's payment type balance changes correctly."""
        description = 'Income transaction'
        value = 500
        self.payment_type.refresh_from_db()
        balance = self.payment_type.balance

        self.client.post(reverse('main'), data={
            'category': self.expense_category.pk,
            'payment_type': self.payment_type.pk,
            'value': value,
            'description': description
        })
        self.payment_type.refresh_from_db()

        self.assertEqual(self.payment_type.balance, balance - value)

    def test_main_POST_add_new_transaction_not_valid(self):
        """Main page. Not valid form data."""
        response = self.client.post(reverse('main'), data={
            'category': self.income_category2.pk,
            'payment_type': self.payment_type2.pk,
            'value': 10**16
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.wallet.transaction_set.all().count(), 0)
        self.assertFormError(response.context_data['form'], 'category',
                             'Select a valid choice. That choice is not one of the available choices.')
        self.assertFormError(response.context_data['form'], 'payment_type',
                             'Select a valid choice. That choice is not one of the available choices.')
        self.assertFormError(response.context_data['form'], 'value',
                             'Ensure that there are no more than 16 digits in total.')

    # Transactions page
    def test_transactions_GET(self):
        response = self.client.get(reverse('transactions'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/transactions.html')

    def test_transactions_GET_queryset(self):
        """Transactions page. Transaction queryset has only user data."""
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=self.payment_type,
                                                 category=self.income_category,
                                                 value=500)
        transaction2 = Transaction.objects.create(wallet=self.wallet2,
                                                  payment_type=self.payment_type2,
                                                  category=self.income_category2,
                                                  value=500)

        response = self.client.get(reverse('transactions'))

        self.assertEqual(self.user.wallet.transaction_set.all().count(),
                         len(response.context_data['transactions']))
        self.assertIn(transaction, response.context_data['transactions'])
        self.assertNotIn(transaction2, response.context_data['transactions'])

    def test_transactions_GET_form_fields(self):
        """Transactions page. Transaction form fields has only user data."""
        response = self.client.get(reverse('transactions'))

        self.assertEqual(response.context_data['form'].fields['payment_type'].queryset.count(), 1)
        self.assertIn(self.payment_type, response.context_data['form'].fields['payment_type'].queryset)
        self.assertNotIn(self.payment_type2, response.context_data['form'].fields['payment_type'].queryset)

        self.assertEqual(response.context_data['form'].fields['category'].queryset.count(), 3)
        self.assertIn(self.income_category, response.context_data['form'].fields['category'].queryset)
        self.assertNotIn(self.income_category2, response.context_data['form'].fields['category'].queryset)

    def test_transactions_POST_filter_date(self):
        """Transactions page. Date filter works correctly."""
        today = timezone.now()
        date_past = today - datetime.timedelta(days=10)
        date_future = today + datetime.timedelta(days=10)
        self.payment_type.refresh_from_db()
        payment_type_card = PaymentType.objects.create(wallet=self.wallet,
                                                       name='Card',
                                                       balance=10000)
        payment_type_credit = PaymentType.objects.create(wallet=self.wallet,
                                                         name='Credit',
                                                         balance=100000)
        transaction_in_past = Transaction.objects.create(wallet=self.wallet,
                                                         payment_type=self.payment_type,
                                                         category=self.income_category,
                                                         value=500,
                                                         date=date_past,
                                                         description='Test')
        transaction_in_present = Transaction.objects.create(wallet=self.wallet,
                                                            payment_type=self.payment_type,
                                                            category=self.income_category,
                                                            value=500,
                                                            description='Test')
        transaction_in_future = Transaction.objects.create(wallet=self.wallet,
                                                           payment_type=self.payment_type,
                                                           category=self.income_category,
                                                           value=500,
                                                           date=date_future,
                                                           description='Test')
        transaction_less_value = Transaction.objects.create(wallet=self.wallet,
                                                            payment_type=self.payment_type,
                                                            category=self.income_category,
                                                            value=100,
                                                            description='Test')
        transaction_middle_value = Transaction.objects.create(wallet=self.wallet,
                                                              payment_type=self.payment_type,
                                                              category=self.income_category,
                                                              value=500,
                                                              description='Test')
        transaction_much_value = Transaction.objects.create(wallet=self.wallet,
                                                            payment_type=self.payment_type,
                                                            category=self.income_category,
                                                            value=1000,
                                                            description='Test')
        transaction_expense_category = Transaction.objects.create(wallet=self.wallet,
                                                                  payment_type=self.payment_type,
                                                                  category=self.expense_category,
                                                                  value=500,
                                                                  description='Test')
        transaction_card_payment_type = Transaction.objects.create(wallet=self.wallet,
                                                                   payment_type=payment_type_card,
                                                                   category=self.income_category,
                                                                   value=500,
                                                                   description='Test')
        transaction_description = Transaction.objects.create(wallet=self.wallet,
                                                             payment_type=self.payment_type,
                                                             category=self.income_category,
                                                             value=500,
                                                             description='Description')

        response = self.client.get(reverse('transactions'), data={
            'date__gte': (date_past + datetime.timedelta(days=5)).strftime('%Y-%m-%d'),
            'date__lte': (date_future - datetime.timedelta(days=5)).strftime('%Y-%m-%d'),
            'value__gte': 400,
            'value__lte': 600,
            'category': self.income_category.pk,
            'payment_type': self.payment_type.pk,
            'description': 'Test'
        })

        # Transactions table
        self.assertEqual(len(response.context_data['transactions']), 2)
        self.assertIn(transaction_in_present, response.context_data['transactions'])
        self.assertIn(transaction_middle_value, response.context_data['transactions'])
        self.assertNotIn(transaction_in_past, response.context_data['transactions'])
        self.assertNotIn(transaction_in_future, response.context_data['transactions'])
        self.assertNotIn(transaction_less_value, response.context_data['transactions'])
        self.assertNotIn(transaction_much_value, response.context_data['transactions'])
        self.assertNotIn(transaction_expense_category, response.context_data['transactions'])
        self.assertNotIn(transaction_card_payment_type, response.context_data['transactions'])
        self.assertNotIn(transaction_description, response.context_data['transactions'])

        # Info panel
        self.assertEqual(response.context_data['balance'],
                         self.payment_type.balance + payment_type_card.balance + payment_type_credit.balance)
        self.assertEqual(response.context_data['income_sum'], 1000)
        self.assertEqual(response.context_data['income_all_time_sum'], 4100)
        self.assertEqual(response.context_data['expense_sum'], 0)
        self.assertEqual(response.context_data['expense_all_time_sum'], 500)

    def test_transaction_details_GET(self):
        """Transaction details page."""
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=self.payment_type,
                                                 category=self.income_category,
                                                 value=500)
        response = self.client.get(reverse('transaction_details', args=[transaction.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/transaction_details.html')

    def test_transaction_details_GET_other_user(self):
        """Transaction details page. Other user data."""
        transaction = Transaction.objects.create(wallet=self.wallet2,
                                                 payment_type=self.payment_type,
                                                 category=self.income_category,
                                                 value=500)

        response = self.client.get(reverse('transaction_details', args=[transaction.pk]))

        self.assertEqual(response.status_code, 403)

    def test_update_transaction_GET(self):
        """Transaction editing page."""
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=self.payment_type,
                                                 category=self.income_category,
                                                 value=500)
        response = self.client.get(reverse('update_transaction', args=[transaction.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/update_transaction.html')

    def test_update_transaction_GET_other_user(self):
        """Transaction editing page. Other user data."""
        transaction = Transaction.objects.create(wallet=self.wallet2,
                                                 payment_type=self.payment_type2,
                                                 category=self.income_category2,
                                                 value=500)
        response = self.client.get(reverse('update_transaction', args=[transaction.pk]))

        self.assertEqual(response.status_code, 403)

    def test_update_transaction_POST(self):
        """Transaction editing page. New name saves correctly."""
        payment_type = PaymentType.objects.create(wallet=self.wallet,
                                                  name='Payment type for transaction',
                                                  balance=1000)
        payment_type_for_update = PaymentType.objects.create(wallet=self.wallet,
                                                             name='Payment type for transaction. Update')
        category_for_update = Category.objects.create(wallet=self.wallet,
                                                      name='Category for transaction. Update',
                                                      type='Income')
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=payment_type,
                                                 category=self.income_category,
                                                 value=1000)

        response = self.client.post(reverse('update_transaction', args=[transaction.pk]), data={
            'payment_type': payment_type_for_update.pk,
            'category': category_for_update.pk,
            'value': 500,
            'date': transaction.date
        })
        transaction.refresh_from_db()
        payment_type.refresh_from_db()
        payment_type_for_update.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(transaction.payment_type, payment_type_for_update)
        self.assertEqual(transaction.category, category_for_update)
        self.assertEqual(transaction.value, 500)
        self.assertEqual(payment_type.balance, 0)
        self.assertEqual(payment_type_for_update.balance, 500)

    def test_update_transaction_POST_not_valid(self):
        """Transaction editing page. Not valid data."""
        payment_type = PaymentType.objects.create(wallet=self.wallet,
                                                  name='Payment type for transaction.',
                                                  balance=1000)
        payment_type_for_update = PaymentType.objects.create(wallet=self.wallet2,
                                                             name='Payment type for transaction. Update. Not valid')
        category_for_update = Category.objects.create(wallet=self.wallet,
                                                      name='Category for update transaction',
                                                      type='Expense')
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=payment_type,
                                                 category=self.income_category,
                                                 value=1000)

        response = self.client.post(reverse('update_transaction', args=[transaction.pk]), data={
            'payment_type': payment_type_for_update.pk,
            'category': category_for_update.pk,
            'value': 10**16,
            'date': 'test'
        })
        transaction.refresh_from_db()
        payment_type.refresh_from_db()
        payment_type_for_update.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(transaction.payment_type, payment_type)
        self.assertEqual(transaction.category, self.income_category)
        self.assertEqual(transaction.value, 1000)
        self.assertEqual(payment_type.balance, 1000)
        self.assertEqual(payment_type_for_update.balance, 0)
        self.assertFormError(response.context_data['form'], 'payment_type',
                             'Select a valid choice. That choice is not one of the available choices.')
        self.assertFormError(response.context_data['form'], 'category',
                             'The type of the transaction category cannot be modified.')
        self.assertFormError(response.context_data['form'], 'value',
                             'Ensure that there are no more than 16 digits in total.')
        self.assertFormError(response.context_data['form'], 'date',
                             'Enter a valid date/time.')

    def test_update_transaction_POST_other_user(self):
        """Transaction editing page. Other user data."""
        transaction = Transaction.objects.create(wallet=self.wallet2,
                                                 payment_type=self.payment_type2,
                                                 category=self.income_category2,
                                                 value=1000)

        response = self.client.post(reverse('update_transaction', args=[transaction.pk]), data={
            'value': 400,
        })

        self.assertEqual(response.status_code, 403)

    def test_delete_transaction_GET(self):
        """Transaction deletion page."""
        payment_type = PaymentType.objects.create(wallet=self.wallet,
                                                  name='Payment type for transaction. Delete',
                                                  balance=1000)
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=payment_type,
                                                 category=self.income_category,
                                                 value=500)
        response = self.client.get(reverse('delete_transaction', args=[transaction.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/delete_transaction.html')

    def test_delete_transaction_POST(self):
        """Transaction deletion page."""
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=self.payment_type,
                                                 category=self.income_category,
                                                 value=500)

        response = self.client.post(reverse('delete_transaction', args=[transaction.pk]))
        self.payment_type.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transaction.objects.filter(pk=transaction.pk).exists(), False)
        self.assertEqual(self.payment_type.balance, -500)

    def test_delete_transaction_POST_other_user(self):
        """Transaction deletion page. Other user data"""
        transaction = Transaction.objects.create(wallet=self.wallet2,
                                                 payment_type=self.payment_type2,
                                                 category=self.income_category2,
                                                 value=500)

        response = self.client.post(reverse('delete_transaction', args=[transaction.pk]))

        self.assertEqual(response.status_code, 403)

    # Payment types
    def test_payment_types_GET(self):
        """Payment types page."""
        response = self.client.get(reverse('payment_types'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/payment_types.html')

    def test_payment_types_GET_queryset(self):
        """Payment types page. Payment type queryset has only user data."""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Card')

        response = self.client.get(reverse('payment_types'))

        self.assertEqual(self.user.wallet.paymenttype_set.all().count(),
                         len(response.context_data['payment_types']))
        self.assertIn(payment_type, response.context_data['payment_types'])
        self.assertNotIn(self.payment_type2, response.context_data['payment_types'])

    def test_create_payment_type_GET(self):
        """Payment type creation page"""
        response = self.client.get(reverse('create_payment_type'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/create_payment_type.html')

    def test_create_payment_type_POST(self):
        """Payment type creation page. Payment type saves correctly."""
        payment_type_name = 'New payment type'
        payment_type_balance = 500

        response = self.client.post(reverse('create_payment_type'), data={
            'name': payment_type_name,
            'balance': payment_type_balance,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.wallet.paymenttype_set.all().count(), 2)
        self.assertEqual(self.user.wallet.paymenttype_set.last().name, payment_type_name)
        self.assertEqual(self.user.wallet.paymenttype_set.last().balance, payment_type_balance)

    def test_create_payment_type_POST_not_valid(self):
        """Payment type creating page. Not valid form data."""
        payment_type_name = 'Cash'
        payment_type_balance = str(10**16)

        response = self.client.post(reverse('create_payment_type'), data={
            'name': payment_type_name,
            'balance': payment_type_balance,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.wallet.paymenttype_set.all().count(), 1)
        self.assertFormError(response.context_data['form'], 'name',
                             'A payment type with that name already exists.')
        self.assertFormError(response.context_data['form'], 'balance',
                             'Ensure that there are no more than 16 digits in total.')

    def test_update_payment_type_GET(self):
        """Payment type editing page."""
        response = self.client.get(reverse('update_payment_type', args=[self.payment_type.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/update_payment_type.html')

    def test_update_payment_type_GET_other_user(self):
        """Payment type's editing page. Other user's data."""
        response = self.client.get(reverse('update_payment_type', args=[self.payment_type2.pk]))

        self.assertEqual(response.status_code, 403)

    def test_update_payment_type_POST(self):
        """Payment type editing page. New name saves correctly."""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Payment type for update',
                                                  balance=100)
        payment_type_name = "Payment type's new name"
        balance = payment_type.balance

        response = self.client.post(reverse('update_payment_type', args=[payment_type.pk]), data={
            'name': payment_type_name,
        })
        payment_type.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(payment_type.name, payment_type_name)
        self.assertEqual(payment_type.balance, balance)

    def test_update_payment_type_POST_not_valid(self):
        """Payment type editing page. Not valid data."""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Payment type for update not valid',
                                                  balance=100)
        payment_type_name = 'Payment type for update not valid'

        response = self.client.post(reverse('update_payment_type', args=[payment_type.pk]), data={
            'name': payment_type_name,
        })
        payment_type.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context_data['form'], 'name',
                             'A payment type with that name already exists.')

    def test_update_payment_type_POST_other_user(self):
        """Payment type editing page. Other user data."""
        response = self.client.post(reverse('update_payment_type', args=[self.payment_type2.pk]), data={
            'name': 'Payment type for other user. POST',
        })

        self.assertEqual(response.status_code, 403)

    def test_delete_payment_type_type_GET(self):
        """Payment type deletion page."""
        response = self.client.get(reverse('delete_payment_type', args=[self.payment_type.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/delete_payment_type.html')

    def test_delete_payment_type_GET_form_select_field(self):
        """Payment type deletion page. Payment type form field
        has only user data."""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Payment type for delete. Fields')

        response = self.client.get(reverse('delete_payment_type', args=[payment_type.pk]))

        self.assertEqual(self.user.wallet.paymenttype_set.exclude(pk=payment_type.pk).count(),
                         response.context_data['form'].fields['name'].queryset.count())
        self.assertIn(self.payment_type, response.context_data['form'].fields['name'].queryset)
        self.assertNotIn(payment_type, response.context_data['form'].fields['name'].queryset)
        self.assertNotIn(self.payment_type2, response.context_data['form'].fields['name'].queryset)

    def test_delete_payment_type_GET_other_user(self):
        """Payment type's deletion page. Other user's data."""
        response = self.client.get(reverse('delete_payment_type', args=[self.payment_type2.pk]))

        self.assertEqual(response.status_code, 403)

    def test_delete_payment_type_POST(self):
        """Payment type deleting page. Payment type deletes correctly."""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Payment type for delete',
                                                  balance=100)

        response = self.client.post(reverse('delete_payment_type', args=[payment_type.pk]), data={
            'name': self.payment_type.pk,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.wallet.paymenttype_set.count(), 1)

    def test_delete_payment_type_POST_not_valid(self):
        """Payment type deleting page. Not valid form data."""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Payment type for delete. POST. Not valid',
                                                  balance=100)

        response = self.client.post(reverse('delete_payment_type', args=[payment_type.pk]), data={
            'name': 'Not valid name',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.wallet.paymenttype_set.count(), 2)
        self.assertEqual(response.context_data['form']['name'].errors,
                         ['Select a valid choice. That choice is not one of the available choices.'])

    def test_delete_payment_type_POST_change_transactions_payment_type(self):
        """Payment type deleting page. Existing transactions change their
        payment type after deleting their payment type"""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Payment type for delete',
                                                  balance=100)
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=payment_type,
                                                 category=self.income_category,
                                                 value=500)

        self.client.post(reverse('delete_payment_type', args=[payment_type.pk]), data={
            'name': self.payment_type.pk,
        })
        transaction.refresh_from_db()

        self.assertEqual(transaction.payment_type, self.payment_type)

    def test_delete_payment_type_POST_other_user(self):
        """Payment type deleting page. Other user data."""
        response = self.client.post(reverse('delete_payment_type', args=[self.payment_type2.pk]), data={
            'name': 'Payment type for other user. POST',
        })

        self.assertEqual(response.status_code, 403)

    def test_transfer_between_payment_types_GET(self):
        """Transfer between payment types."""
        response = self.client.get(reverse('transfer_between_payment_types'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/transfer_between_payment_types.html')

    def test_transfer_between_payment_types_GET_form_select_fields(self):
        """Transfer between payment types. Select fields of the transfer form
        should contain only user data"""
        payment_type = PaymentType.objects.create(wallet=self.user.wallet,
                                                  name='Payment type for transfer')

        response = self.client.get(reverse('transfer_between_payment_types'))
        form_payment_type_from_qs = response.context_data['form'].fields['payment_type_from'].queryset
        form_payment_type_to_qs = response.context_data['form'].fields['payment_type_from'].queryset
        user_payment_types = self.user.wallet.paymenttype_set.all()

        self.assertEqual(form_payment_type_from_qs.count(), user_payment_types.count())
        self.assertEqual(form_payment_type_to_qs.count(), user_payment_types.count())
        self.assertIn(payment_type, form_payment_type_from_qs)
        self.assertIn(payment_type, form_payment_type_to_qs)
        self.assertNotIn(self.payment_type2, form_payment_type_from_qs)
        self.assertNotIn(self.payment_type2, form_payment_type_to_qs)

    def test_transfer_between_payment_types_POST(self):
        """Transfer between payment types. Balance changes correctly."""
        payment_type_from = PaymentType.objects.create(wallet=self.user.wallet,
                                                       name='Payment type for transfer. From',
                                                       balance=1000)
        payment_type_to = PaymentType.objects.create(wallet=self.user.wallet,
                                                     name='Payment type for transfer. To',
                                                     balance=1000)
        payment_type_from_balance = payment_type_from.balance
        payment_type_to_balance = payment_type_to.balance
        value = 500

        response = self.client.post(reverse('transfer_between_payment_types'), data={
            'payment_type_from': payment_type_from.pk,
            'payment_type_to': payment_type_to.pk,
            'value': value,
            'description': 'Transfer for test',
        })
        payment_type_from.refresh_from_db()
        payment_type_to.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(payment_type_from.balance, payment_type_from_balance - value)
        self.assertEqual(payment_type_to.balance, payment_type_to_balance + value)

    def test_transfer_between_payment_types_POST_not_valid(self):
        """Transfer between payment types. Balance changes correctly."""
        payment_type_from = PaymentType.objects.create(wallet=self.user2.wallet,
                                                       name='Payment type for transfer. From. Other user',
                                                       balance=1000)
        payment_type_to = PaymentType.objects.create(wallet=self.user2.wallet,
                                                     name='Payment type for transfer. To. Other user',
                                                     balance=1000)

        response = self.client.post(reverse('transfer_between_payment_types'), data={
            'payment_type_from': payment_type_from.pk,
            'payment_type_to': payment_type_to.pk,
            'value': 10**16,
            'description': 'Transfer for test',
        })
        payment_type_from.refresh_from_db()
        payment_type_to.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['form']['payment_type_from'].errors,
                         ['Select a valid choice. That choice is not one of the available choices.'])
        self.assertEqual(response.context_data['form']['payment_type_to'].errors,
                         ['Select a valid choice. That choice is not one of the available choices.'])
        self.assertEqual(response.context_data['form']['value'].errors,
                         ['Ensure that there are no more than 16 digits in total.'])

    # Categories
    def test_categories_GET(self):
        """Categories page."""
        response = self.client.get(reverse('categories'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/categories.html')

    def test_categories_GET_queryset(self):
        """Categories page. Category queryset has only user data."""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category for queryset',
                                           type='Expense')

        response = self.client.get(reverse('categories'))

        self.assertEqual(self.user.wallet.category_set.all().count() - 1,
                         response.context_data['categories'].count())
        self.assertIn(category, response.context_data['categories'])
        self.assertNotIn(self.payment_type2, response.context_data['categories'])

    def test_create_category_GET(self):
        """Category type creation page"""
        response = self.client.get(reverse('create_category'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/create_category.html')

    def test_create_category_POST(self):
        """Category creation page. Category saves correctly."""
        category_name = 'New payment type'
        category_type = 'Expense'

        response = self.client.post(reverse('create_category'), data={
            'name': category_name,
            'type': category_type,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.wallet.category_set.all().count(), 4)
        self.assertEqual(self.user.wallet.category_set.last().name, category_name)
        self.assertEqual(self.user.wallet.category_set.last().type, category_type)

    def test_create_category_POST_not_valid(self):
        """Category creation page. Not valid form data."""
        category_name = 'Income'
        category_type = 'Not valid type'

        response = self.client.post(reverse('create_category'), data={
            'name': category_name,
            'type': category_type,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.wallet.category_set.all().count(), 3)
        self.assertFormError(response.context_data['form'], 'name',
                             'A category with that name already exists.')
        self.assertFormError(response.context_data['form'], 'type',
                             'Select a valid choice. Not valid type is not one of the available choices.')

    def test_update_category_GET(self):
        """Category' editing page."""
        response = self.client.get(reverse('update_category', args=[self.income_category.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/update_category.html')

    def test_update_category_GET_other_user(self):
        """Category's editing page. Other user data."""
        response = self.client.get(reverse('update_category', args=[self.income_category2.pk]))

        self.assertEqual(response.status_code, 403)

    def test_update_category_POST(self):
        """Category editing page. New name saves correctly."""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category type for update',
                                           type='Expense')
        category_name = "Category's new name"

        response = self.client.post(reverse('update_category', args=[category.pk]), data={
            'name': category_name,
        })
        category.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(category.name, category_name)

    def test_update_category_POST_not_valid(self):
        """Category editing page. Not valid data."""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category type for update. Not valid',
                                           type='Expense')
        category_name = "Category type for update. Not valid"

        response = self.client.post(reverse('update_category', args=[category.pk]), data={
            'name': category_name,
        })
        category.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context_data['form'], 'name',
                             'A category with that name already exists.')

    def test_update_category_POST_other_user(self):
        """Category editing page. Other user data."""
        response = self.client.post(reverse('update_category', args=[self.income_category2.pk]), data={
            'name': 'Category for other user. POST',
        })

        self.assertEqual(response.status_code, 403)

    def test_delete_category_GET(self):
        """Category deletion page."""
        response = self.client.get(reverse('delete_category', args=[self.income_category.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/delete_category.html')

    def test_delete_category_GET_form_expense_select_field(self):
        """Category deletion page. Expense category form field
        has only user's data."""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category for delete. Expense type. Fields',
                                           type='Expense')

        response = self.client.get(reverse('delete_category', args=[category.pk]))
        self.assertEqual(self.user.wallet.category_set.all().filter(type='Expense').exclude(pk=category.pk).count(),
                         response.context_data['form'].fields['name'].queryset.count())
        self.assertIn(self.expense_category, response.context_data['form'].fields['name'].queryset)
        self.assertNotIn(category, response.context_data['form'].fields['name'].queryset)
        self.assertNotIn(self.expense_category2, response.context_data['form'].fields['name'].queryset)

    def test_delete_category_GET_form_income_select_field(self):
        """Category deletion page. Income category form field
        has only user data."""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category for delete. Income type. Fields',
                                           type='Income')

        response = self.client.get(reverse('delete_category', args=[category.pk]))
        self.assertEqual(self.user.wallet.category_set.all().filter(type='Income').exclude(pk=category.pk).count(),
                         response.context_data['form'].fields['name'].queryset.count())
        self.assertIn(self.income_category, response.context_data['form'].fields['name'].queryset)
        self.assertNotIn(category, response.context_data['form'].fields['name'].queryset)
        self.assertNotIn(self.income_category2, response.context_data['form'].fields['name'].queryset)

    def test_delete_category_GET_other_user(self):
        """Category deletion page. Other user data."""
        response = self.client.get(reverse('delete_category', args=[self.income_category2.pk]))

        self.assertEqual(response.status_code, 403)

    def test_delete_category_POST(self):
        """Category deleting page. Category deletes correctly."""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category for delete. POST',
                                           type='Income')

        response = self.client.post(reverse('delete_category', args=[category.pk]), data={
            'name': self.income_category.pk,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.wallet.category_set.count(), 3)

    def test_delete_category_POST_not_valid(self):
        """Category deleting page. Not valid form data."""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category for delete. POST. Not valid',
                                           type='Income')

        response = self.client.post(reverse('delete_category', args=[category.pk]), data={
            'name': 'Not valid category',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.wallet.category_set.count(), 4)
        self.assertEqual(response.context_data['form']['name'].errors,
                         ['Select a valid choice. That choice is not one of the available choices.'])

    def test_delete_category_POST_change_transactions_category(self):
        """Category deleting page. Existing transactions change their
        category after deleting their category"""
        category = Category.objects.create(wallet=self.user.wallet,
                                           name='Category for delete. POST. Change in transactions',
                                           type='Income')
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 payment_type=self.payment_type,
                                                 category=category,
                                                 value=500)

        self.client.post(reverse('delete_category', args=[category.pk]), data={
            'name': self.income_category.pk,
        })
        transaction.refresh_from_db()

        self.assertEqual(transaction.category, self.income_category)

    def test_delete_category_POST_other_user(self):
        """Category deleting page. Other user data."""
        response = self.client.post(reverse('delete_category', args=[self.income_category2.pk]), data={
            'name': 'Category for other user. POST',
        })

        self.assertEqual(response.status_code, 403)

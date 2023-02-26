from django.db import models
from django.conf import settings
from django.utils import timezone


class Wallet(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner.pk} - {self.owner} wallet'


class PaymentType(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(default=0, max_digits=16, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['wallet', 'name'], name='unique_name_for_payment_type')
        ]


class Category(models.Model):
    transition_types = [
        ('Expense', 'Expense'),
        ('Income', 'Income')
    ]
    name = models.CharField(max_length=100)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=transition_types)
    service = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['wallet', 'name'], name='unique_name_for_category')
        ]


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=16, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.wallet}: {self.category} - {self.value} ({self.description})'

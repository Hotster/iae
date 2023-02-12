from django.contrib import admin
from accounting.models import *

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(PaymentType)

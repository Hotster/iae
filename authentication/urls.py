from django.urls import path
from authentication.views import *

urlpatterns = [
    path('registry', Registry.as_view(), name='registry'),
    path('login', Login.as_view(), name='login'),
    path('logout', user_logout, name='logout'),
]

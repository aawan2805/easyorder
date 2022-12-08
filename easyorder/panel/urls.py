from django.urls import path

from panel.views import *

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('home', Home.as_view(), name='home')
]

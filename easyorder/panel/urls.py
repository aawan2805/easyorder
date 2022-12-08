from django.urls import path

from panel.views import *

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('home', Home.as_view(), name='home'),
    path('add-plato', AddDishView.as_view(), name='add-plato'),
]

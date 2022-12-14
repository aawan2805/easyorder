from django.urls import path, include

from panel.views import *

urlpatterns = [
    # path('', LoginUser.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('platos', Platos.as_view(), name='platos'),
    path('add-plato', AddDishView.as_view(), name='add-plato'),
    path('edit-plato/<uuid:dish_id>', EditDish.as_view(), name='edit-plato'),
    path('delete-plato/<uuid:dish_id>', DeleteDish.as_view(), name='delete-plato'),
]

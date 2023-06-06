from django.urls import path, include

from panel.views import *

urlpatterns = [
    path('', Platos.as_view(), name='home'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/register/<uuid:register_token>', RegisterView.as_view(), name='register-new-brand'),

    path('home', HomeView.as_view(), name='stats'),

    path('platos', Platos.as_view(), name='platos'),
    path('add-plato', AddDishView.as_view(), name='add-plato'),
    path('edit-plato/<uuid:dish_id>', EditDish.as_view(), name='edit-plato'),
    path('delete-plato/<uuid:dish_id>', DeleteDish.as_view(), name='delete-plato'),

    path('categorias', Categories.as_view(), name='categorias'),
    path('add-categoria', AddCategoryView.as_view(), name='add-category'),
    path('edit-categoria/<uuid:category_id>', EditCategory.as_view(), name='edit-category'),
    path('delete-category/<uuid:category_id>', DeleteCategory.as_view(), name='delete-category'),

    path('orders', OrdersView.as_view(), name='orders'),
    path('change-order-status/<int:order_id>', ChangeOrderStatus.as_view(), name='change-order-status'),

    path('qr', QRBrand.as_view(), name='qr'),    
]

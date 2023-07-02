from django.urls import path, include
from django.contrib.auth import views as auth_views
from panel.views import *


urlpatterns = [
    path('', Platos.as_view(), name='home'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('password_reset/', auth_views.PasswordResetView.as_view(extra_context={'extra_context': '/accounts/login'}), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

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

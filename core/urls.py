from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('cart/', cart, name='cart'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('orders/', orders, name='orders'),

    # Categories
    path('books/fiction/', fiction_books, name='fiction'),
    path('books/non-fiction/', non_fiction_books, name='non_fiction'),
    path('books/nepali/', nepali_books, name='nepali'),

    # Product detail
    path('product/<str:product_type>/<int:pk>/', product_detail, name='product_detail'),

    # Cart
    path('cart/add/<str:product_type>/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),

    # Payments
    path('esewa/pay/', initiate_esewa, name='initiate_esewa'),
    path('esewa/success/', esewa_success, name='esewa_success'),
    path('esewa/failure/', esewa_failure, name='esewa_failure'),

    # Auth
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
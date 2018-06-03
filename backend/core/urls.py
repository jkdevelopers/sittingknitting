from django.shortcuts import render, redirect
from django.urls import path
from .views import *

urlpatterns = [
    path('', lambda r: redirect('home')),
    path('home/', home, name='home'),
    path('contacts/', contacts, name='contacts'),
    path('info/', info, name='info'),
    path('edit/<int:pk>/', component_edit, name='edit'),
    path('action/', component_action, name='action'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('subscribe/', subscribe, name='subscribe'),
    path('products/category/<int:pk>/', products, name='products'),
    path('products/', products, name='all_products'),
    path('product/<int:pk>/', product, name='product'),
    path('cart/<action>/<slug:data>/', cart_action, name='cart_action'),
    path('cart/', cart, name='cart'),
    path('policy/', policy, name='policy'),
    path('agreement/', agreement, name='agreement'),
]

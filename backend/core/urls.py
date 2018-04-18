from django.shortcuts import render, redirect
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', lambda r: redirect('home')),
    url(r'^home/$', home, name='home'),
    url(r'^edit/(?P<pk>\d+)/$', component_edit, name='edit'),
    url(r'^action/$', component_action, name='action'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^register/$', register, name='register'),
    url(r'^subscribe/$', subscribe, name='subscribe'),
    url(r'^product/(?P<pk>\d+)/$', product, name='product'),
    url(r'^products/(?:category/(?P<pk>\d+)/)?$', products, name='products'),
]

from django.shortcuts import render, redirect
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', lambda r: redirect('home')),
    url(r'^home/$', home, name='home'),
    url(r'^edit/(?P<pk>\d+)/$', component_edit, name='edit'),
    url(r'^action/$', component_action, name='action'),
]

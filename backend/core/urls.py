from django.shortcuts import render, redirect
from django.conf.urls import url
from .views import component_edit

urlpatterns = [
    url(r'^$', lambda r: redirect('home')),
    url(r'^home/$', lambda r: render(r, 'home.html'), name='home'),
    url(r'^edit/(?P<pk>\d+)/$', component_edit, name='edit'),
    url(r'^test/$', lambda r: render(r, 'test.html'), name='test'),
]

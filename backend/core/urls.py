from django.conf.urls import url
from django.shortcuts import render, redirect

urlpatterns = [
    url(r'^$', lambda r: redirect('home')),
    url(r'^home/$', lambda r: render(r, 'home.html'), name='home'),
    url(r'^test/$', lambda r: render(r, 'test.html'), name='test'),
]

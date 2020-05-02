from django.urls import path

from .views import login

urlpatterns = [
    path('login', login.login, name='login'),
    path('logout', login.logout, name='logout')
]

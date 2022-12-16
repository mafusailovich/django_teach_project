from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import IndexView, upgrade_me

urlpatterns = [
    path('', IndexView.as_view()),
    path('upgrade/', upgrade_me, name='upgrade')
]
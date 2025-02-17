from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("list", views.list, name="list"),
    path("view", views.view, name="view"),
    path("average", views.average, name="average"),
    path("rate", views.rate, name="rate"),
]
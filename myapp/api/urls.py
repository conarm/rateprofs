from django.urls import path

from . import views

urlpatterns = [
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("list", views.list_view, name="list"),
    path("view", views.view_view, name="view"),
    path("average", views.average_view, name="average"),
    path("rate", views.rate_view, name="rate"),
]
from django.urls import path

from butterfly.core import views

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="login"),
]

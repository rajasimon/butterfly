from django.urls import path

from butterfly.core import views

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("status/", views.StatusAPIView.as_view(), name="status"),
    path("status/<pk>/", views.StatusAPIView.as_view(), name="status-detail"),
    path("friends/", views.FriendsListViewSet.as_view({"get": "list"}), name="friends"),
    path(
        "received/", views.ReceivedListViewSet.as_view({"get": "list"}), name="received"
    ),
    path("users/", views.UserListAPIView.as_view(), name="users"),
]

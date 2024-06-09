from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from butterfly.core.models import Friend, Profile
from butterfly.core.serializer import FriendSerializer, ProfileSerializer
from butterfly.core.throttles import FriendRequestThrottle


class RegisterAPIView(APIView):
    """
    Accept only email from the payload and create the user to accommodate
    the requirements.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.save()

            Token.objects.create(user=profile)
            return Response({"detail": "User created successfully"})

        return Response(serializer.errors)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        # Password is optional here.
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if user is not None:
            data = {"token": user.auth_token.key}
            return Response(data, status=status.HTTP_200_OK)

        else:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class StatusAPIView(APIView):
    throttle_classes = [FriendRequestThrottle]

    def get_object(self, pk):
        return get_object_or_404(Friend, pk=pk)

    def post(self, request):
        data = request.data.copy()
        data["owner"] = request.user.id

        serializer = FriendSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        instance = self.get_object(pk)
        serializer = FriendSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendsListViewSet(ModelViewSet):
    def list(self, request):
        queryset = Friend.objects.filter(
            owner=request.user, status=Friend.StatusChoice.ACCEPT
        )
        serializer = FriendSerializer(queryset, many=True)
        return Response(serializer.data)


class ReceivedListViewSet(ModelViewSet):
    def list(self, request):
        queryset = Friend.objects.filter(
            owner=request.user, status=Friend.StatusChoice.SEND
        )
        serializer = FriendSerializer(queryset, many=True)
        return Response(serializer.data)


class UserListPagination(PageNumberPagination):
    page_size = 10


class UserListAPIView(ListAPIView):
    queryset = Profile.objects.order_by("-name")
    serializer_class = ProfileSerializer
    filter_backends = [SearchFilter]
    search_fields = ["email", "name"]
    pagination_class = UserListPagination

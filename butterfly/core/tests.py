from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from factory.django import DjangoModelFactory
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from butterfly.core.models import Friend, Profile

EMAIL = "rajasimonio@gmail.com"
NAME = "Raja Simon"


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile


class FriendFactory(DjangoModelFactory):
    class Meta:
        model = Friend


class RegisterTests(APITestCase):
    def test_create_account(self):
        url = reverse("register")
        data = {"email": EMAIL}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test if the email is already exists in this case return an error.
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.json()["email"][0],
            "profile with this email address already exists.",
        )


class LoginTests(APITestCase):
    def test_login_account(self):
        profile = ProfileFactory(email=EMAIL)

        # Since I am using factory boy making sure the token is exists.
        token = Token.objects.create(user=profile)

        url = reverse("login")
        data = {"email": EMAIL}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["token"], token.key)

    def test_login_account_with_password(self):
        # Create the profile with the password
        profile = ProfileFactory(email=EMAIL)
        profile.set_password("password")
        profile.save()

        # Since I am using factory boy making sure the token is exists.
        token = Token.objects.create(user=profile)

        url = reverse("login")
        data = {"email": EMAIL, "password": "password"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["token"], token.key)

    def test_login_account_with_wrong_password(self):
        # Create the profile with the password
        profile = ProfileFactory(email=EMAIL)
        profile.set_password("password")
        profile.save()

        # Since I am using factory boy making sure the token is exists.
        Token.objects.create(user=profile)

        url = reverse("login")
        data = {"email": EMAIL, "password": "wrong_password"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Invalid credentials")


class StatusTest(APITestCase):
    def test_friend_send_request(self):
        """
        Create a friend request.
        """
        url = reverse("status")

        # Prepare the owner and friend1
        owner = ProfileFactory(email=EMAIL)
        friend1 = ProfileFactory()

        token = Token.objects.create(user=owner)

        # Setting up the APIClient
        client = APIClient()
        client.force_authenticate(user=owner, token=token)

        data = {"status": "SEND", "profile": friend1.id}
        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "SEND")
        self.assertEqual(response.data["profile"], friend1.id)

    def test_friend_reject_request(self):
        """
        Reject a friend request
        """

        # Prepare the owner and friend1
        owner = ProfileFactory(email=EMAIL)
        friend = ProfileFactory(email="test@gmail.com")
        friend_obj = FriendFactory(owner=owner, profile=friend)

        data = {"status": "REJECT", "profile": friend.id}

        token = Token.objects.create(user=owner)
        client = APIClient()
        client.force_authenticate(user=owner, token=token)

        url = reverse("status-detail", kwargs={"pk": friend_obj.id})
        response = client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "REJECT")
        self.assertEqual(response.data["profile"], friend.id)


class FriendsListAPITest(APITestCase):
    def test_list(self):
        """
        Return friends list from the database
        """
        profile = ProfileFactory(email=EMAIL)
        for i in range(5):
            FriendFactory(
                status="ACCEPT",
                owner=profile,
                profile=ProfileFactory(email=f"test{i}@mail.com"),
            )

        for i in range(5, 10):
            FriendFactory(
                status="REJECT",
                owner=profile,
                profile=ProfileFactory(email=f"test{i}@mail.com"),
            )

        token = Token.objects.create(user=profile)
        client = APIClient()
        client.force_authenticate(user=profile, token=token)

        url = reverse("friends")
        resp = client.get(url, format="json")
        response = resp.json()

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response), 5)


class ReceivedListAPITest(APITestCase):
    def test_list(self):
        """
        Return friends list from the database
        """
        profile = ProfileFactory(email=EMAIL)
        for i in range(5):
            FriendFactory(
                status="SEND",
                owner=profile,
                profile=ProfileFactory(email=f"test{i}@mail.com"),
            )

        for i in range(5, 10):
            FriendFactory(
                status="ACCEPT",
                owner=profile,
                profile=ProfileFactory(email=f"test{i}@mail.com"),
            )

        token = Token.objects.create(user=profile)
        client = APIClient()
        client.force_authenticate(user=profile, token=token)

        url = reverse("received")
        resp = client.get(url, format="json")
        response = resp.json()

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response), 5)


class FriendRequestThrottleTestCase(APITestCase):
    def setUp(self):
        self.profile = ProfileFactory(email=EMAIL)
        token = Token.objects.create(user=self.profile)
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile, token=token)
        self.url = reverse(
            "status"
        )  # Ensure this URL is correct and mapped to the throttled view

    def test_throttle_limit_exceeded(self):
        now = timezone.now()
        FriendFactory(
            owner=self.profile,
            profile=ProfileFactory(email="profile3@gmail.com"),
            created=now - timedelta(seconds=30),
        )
        FriendFactory(
            owner=self.profile,
            profile=ProfileFactory(email="profile2@gmail.com"),
            created=now - timedelta(seconds=20),
        )
        FriendFactory(
            owner=self.profile,
            profile=ProfileFactory(email="profile1@gmail.com"),
            created=now - timedelta(seconds=10),
        )

        profile0 = ProfileFactory(email="profile0@gmai.com")

        data = {"status": "SEND", "profile": profile0.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_throttle_recent_request_within_time(self):
        now = timezone.now()
        FriendFactory(
            owner=self.profile,
            profile=ProfileFactory(email="profile1@gmail.com"),
            created=now - timedelta(minutes=1, seconds=10),
        )

        profile2 = ProfileFactory(email="profile2@gmail.com")

        data = {"status": "SEND", "profile": profile2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_throttle_recent_request_within_limit(self):
        test_profile = ProfileFactory(email="tesrer@gmail.com")
        data = {"status": "SEND", "profile": test_profile.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserListTestCase(APITestCase):
    def setUp(self):
        self.profile = ProfileFactory(email=EMAIL, name="")
        token = Token.objects.create(user=self.profile)
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile, token=token)
        self.url = reverse("users")

    def test_search_empty(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_search_name(self):
        # Creating a differnt name profile
        ProfileFactory(email="test@gmail.com")
        param = {"search": "Sim"}
        response = self.client.get(self.url, data=param, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_search_email(self):
        # Creating a differnt name profile
        ProfileFactory(email="test@gmail.com", name="Test Gmail")
        param = {"search": "Test"}
        response = self.client.get(self.url, data=param, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

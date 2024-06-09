from rest_framework.serializers import ModelSerializer

from butterfly.core.models import Friend, Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "email"]


class FriendSerializer(ModelSerializer):
    class Meta:
        model = Friend
        fields = ["id", "owner", "profile", "status"]

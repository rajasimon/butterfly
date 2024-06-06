from django.contrib.auth.backends import BaseBackend

from butterfly.core.models import Profile


class EmailPasswordBackend(BaseBackend):

    def authenticate(self, request, email=None, password=None):
        print(email, password)
        # Use the email get the profile
        profile = Profile.objects.filter(email=email).first()

        if not profile:
            return None

        if profile.check_password(password):
            return profile

        return None

    def get_user(self, user_id):
        try:
            return Profile.objects.get(pk=user_id)
        except Profile.DoesNotExist:
            return None

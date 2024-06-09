from django.contrib.auth.backends import BaseBackend

from butterfly.core.models import Profile


class EmailPasswordBackend(BaseBackend):

    def authenticate(self, request, email=None, password=None):
        """
        When given the email return the user profile. Password is optional if
        it's given then assert the truths of it.
        """
        # Use the email get the profile
        profile = Profile.objects.filter(email=email).first()

        if not profile:
            return None

        if password:
            if profile.check_password(password):
                return profile

            return None

        return profile

    def get_user(self, user_id):
        try:
            return Profile.objects.get(pk=user_id)
        except Profile.DoesNotExist:
            return None

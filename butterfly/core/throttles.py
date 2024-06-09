"""
Throttle used here to restrict user to not send more than 3 requests per minute.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import throttling

from butterfly.core.models import Friend


class FriendRequestThrottle(throttling.BaseThrottle):
    def allow_request(self, request, view):
        if request.method == "POST":
            now = timezone.now()
            recent_requests = Friend.objects.filter(
                owner=request.user, created__gte=now - timedelta(minutes=3)
            )
            if recent_requests.count() >= 3:
                return False
        return True

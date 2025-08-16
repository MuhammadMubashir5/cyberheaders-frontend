# api/permissions.py
from rest_framework import permissions
from django.conf import settings


class HasValidAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('api-key')
        if not api_key:
            return False

        # Check if API key exists in settings
        return api_key in settings.API_KEYS
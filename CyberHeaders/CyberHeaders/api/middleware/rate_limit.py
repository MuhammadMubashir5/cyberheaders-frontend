from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import re
import time


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        api_key = request.headers.get('api-key', 'anonymous')
        rate_limit = self.get_rate_limit(api_key)

        if not rate_limit:
            return self.get_response(request)

        limit, period = self.parse_rate(rate_limit)
        key = f'ratelimit:{api_key}:{request.path}'

        current = cache.get(key, 0)
        if current >= limit:
            return JsonResponse(
                {'detail': 'Too many requests. Please try again later.'},
                status=429
            )

        cache.set(key, current + 1, period)
        return self.get_response(request)

    def get_rate_limit(self, api_key):
        if api_key in settings.API_KEYS:
            return settings.API_KEYS[api_key]['limit']
        return settings.RATE_LIMIT

    def parse_rate(self, rate):
        if '/' not in rate:
            return (int(rate), 60)  # Default to per minute

        num, period = rate.split('/')
        num = int(num)

        if period == 'second':
            period_seconds = 1
        elif period == 'minute':
            period_seconds = 60
        elif period == 'hour':
            period_seconds = 3600
        elif period == 'day':
            period_seconds = 86400
        else:
            period_seconds = 60  # Default to minute

        return (num, period_seconds)
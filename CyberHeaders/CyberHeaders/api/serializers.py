from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from datetime import datetime
import pytz


class URLRequestSerializer(serializers.Serializer):
    """
    Validates and processes incoming scan requests
    Example:
    {
        "url": "https://example.com",
        "include_gemini_analysis": true,
        "deep_scan": false,
        "pdf_generation": false
    }
    """
    url = serializers.CharField(
        max_length=2048,
        help_text="The URL to analyze (must include http:// or https://)"
    )
    include_gemini_analysis = serializers.BooleanField(
        default=False,
        help_text="Whether to include AI-powered analysis from Gemini"
    )
    deep_scan = serializers.BooleanField(
        default=False,
        help_text="Whether to perform DNS-level deep scanning"
    )
    pdf_generation = serializers.BooleanField(
        default=False,
        help_text="Whether to generate a PDF report"
    )

    def validate_url(self, value):
        """Validate URL format and protocol"""
        validator = URLValidator(schemes=['http', 'https'])

        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must include http:// or https://")

        try:
            validator(value)
        except ValidationError as e:
            raise serializers.ValidationError(f"Invalid URL: {str(e)}")

        return value


class EnhancedAnalysisResponseSerializer(serializers.Serializer):
    """
    Serializes comprehensive security analysis results
    Example response:
    {
        "url": "https://example.com",
        "status_code": 200,
        "security_score": 85,
        "score_breakdown": {...},
        "headers": {...},
        "analysis": {...},
        "ssl": {...},
        "dns": {...},
        "recommendations": [...],
        "passed_checks": [...],
        "failed_checks": [...],
        "risk_level": "Low",
        "timestamp": "2023-11-20T12:00:00Z",
        "gemini_analysis": "..."
    }
    """
    url = serializers.URLField(
        max_length=2048,
        help_text="The analyzed URL"
    )
    status_code = serializers.IntegerField(
        min_value=100,
        max_value=599,
        help_text="HTTP status code from the target site"
    )
    security_score = serializers.IntegerField(
        min_value=0,
        max_value=100,
        help_text="Overall security score (0-100)"
    )
    score_breakdown = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Detailed scoring by category"
    )
    headers = serializers.DictField(
        child=serializers.CharField(),
        help_text="Raw HTTP headers from the response"
    )
    analysis = serializers.DictField(
        help_text="Detailed header analysis results"
    )
    ssl = serializers.DictField(
        help_text="SSL/TLS scan results"
    )
    dns = serializers.DictField(
        required=False,
        help_text="DNS scan results (only for deep scans)"
    )
    recommendations = serializers.ListField(
        child=serializers.CharField(max_length=500),
        help_text="List of security recommendations"
    )
    passed_checks = serializers.ListField(
        child=serializers.CharField(max_length=200),
        help_text="Security checks that passed"
    )
    failed_checks = serializers.ListField(
        child=serializers.CharField(max_length=200),
        help_text="Security checks that failed"
    )
    risk_level = serializers.ChoiceField(
        choices=['Low', 'Medium', 'High'],
        help_text="Overall risk assessment"
    )
    timestamp = serializers.DateTimeField(
        default_timezone=pytz.UTC,
        help_text="When the analysis was performed"
    )
    gemini_analysis = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="AI-generated analysis if requested"
    )

    def validate_timestamp(self, value):
        """Ensure timestamp is in UTC and properly formatted"""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                raise serializers.ValidationError("Invalid ISO 8601 format")

        if value.tzinfo != pytz.UTC:
            value = value.astimezone(pytz.UTC)

        return value.isoformat().replace('+00:00', 'Z')
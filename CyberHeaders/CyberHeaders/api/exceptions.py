# api/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 403:
            response.data = {
                'error': 'API key missing or invalid',
                'status_code': response.status_code
            }
    return response


class RequestFailedError(Exception):
    """Raised when an HTTP request to a target website fails"""
    pass

class AnalysisError(Exception):
    """Raised when security analysis fails"""
    pass

class InvalidURLError(Exception):
    """Raised when invalid URL is provided"""
    pass

class GeminiAIError(Exception):
    """Raised when Gemini AI analysis fails"""
    pass

class PDFGenerationError(Exception):
    """Raised when PDF report generation fails"""
    pass
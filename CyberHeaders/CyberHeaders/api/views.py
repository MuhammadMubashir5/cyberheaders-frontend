from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from .serializers import URLRequestSerializer, EnhancedAnalysisResponseSerializer
from .utils.analysis import analyze_website
from .utils.pdf import generate_pdf_report
from .exceptions import RequestFailedError, AnalysisError  # Added imports
import uuid
import logging
from api.permissions import HasValidAPIKey

logger = logging.getLogger(__name__)

class AnalyzeView(APIView):
    def post(self, request):
        serializer = URLRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Run async function in sync view
            result = async_to_sync(analyze_website)(
                url=serializer.validated_data['url'],
                include_gemini_analysis=serializer.validated_data['include_gemini_analysis'],
                deep_scan=serializer.validated_data['deep_scan']
            )

            # Handle optional PDF generation
            if serializer.validated_data['pdf_generation']:
                filename = f"CyberHeaders_{uuid.uuid4().hex}.pdf"
                output_path = f"{filename}"
                try:
                    generate_pdf_report(result, output_path=output_path)
                    return FileResponse(
                        open(output_path, 'rb'),
                        content_type='application/pdf',
                        filename=filename
                    )
                except Exception as e:
                    logger.error(f"PDF generation failed: {e}")
                    return Response(
                        {"detail": "PDF generation failed"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            # Serialize and return JSON response
            response_serializer = EnhancedAnalysisResponseSerializer(data=result)
            if response_serializer.is_valid():
                return Response(response_serializer.validated_data)

            return Response(
                response_serializer.errors,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except RequestFailedError as e:
            logger.error(f"Request failed: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except AnalysisError as e:
            logger.error(f"Analysis error: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"detail": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "version": "3.0"})

def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': response.data,
            'status_code': response.status_code
        }

    return response
from rest_framework.views import exception_handler
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    logger.error(f"Exception occurred: {exc} in {context['view'].__class__.__name__}")

    if response is not None:
        return format_error_response(response, exc)

    return JsonResponse({
        'error': True,
        'detail': str(exc),
        'code': 'server_error'
    }, status=500)


def format_error_response(response, exc):
    if hasattr(response, 'data'):
        if isinstance(response.data, dict) and 'detail' in response.data:
            response.data = {
                'error': True,
                'detail': response.data['detail'],
                'code': getattr(exc, 'default_code', 'error')
            }
        else:
            response.data = {
                'error': True,
                'detail': response.data,
                'code': getattr(exc, 'default_code', 'error')
            }
    return response

from rest_framework.exceptions import APIException
from rest_framework import status


class URLValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid URL format'
    default_code = 'invalid_url'


class ShortCodeExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Custom short code already exists'
    default_code = 'short_code_exists'


class ShortCodeNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Short URL not found'
    default_code = 'short_code_not_found'


class RateLimitExceededError(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Too many requests, please try again later'
    default_code = 'rate_limit_exceeded'


class UnauthorisedError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Unauthorised short url'
    default_code = 'unauthorised_short_url'


class ForbiddenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to access the short url'
    default_code = 'permission_denied_for_the_short_url'

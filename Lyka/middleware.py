
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.response import Response
from rest_framework import status
from lyka_user.models import BlacklistedToken


class TokenBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META['HTTP_AUTHORIZATION']
            token = auth_header.split(' ')[1]

            if is_token_blacklisted(token):
                return Response({'message': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)

        response = self.get_response(request)
        return response

def is_token_blacklisted(token):
    if BlacklistedToken.objects.filter(token=token).exists():
        return True
    else:
        return False
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token
from .models import UserToken
from rest_framework import status

class AuthenticationToken(TokenAuthentication):
    model = UserToken

    def authenticate(self, request):
        data = request.data

        auth_token = request.META.get("HTTP_AUTHORIZATION") # when doing lookups in the request META dict, the headers that it's actually looking for are with out the preceeding HTTP.
        response = {}

        if auth_token == None or auth_token == '':
            response['message'] = "Token is required."
            response['status'] = status.HTTP_401_UNAUTHORIZED
            raise exceptions.AuthenticationFailed(response)

        else:
            if not auth_token.startswith('Token '):
                response['message'] = "Token format is invalid."
                response['status'] = status.HTTP_401_UNAUTHORIZED
                raise exceptions.AuthenticationFailed(response)

        auth_token = auth_token.split(' ') # Convert string into list.

        token = UserToken.objects.filter(key = auth_token[1]).first() # Get the first object from Database.

        if not token:

            response['message'] = "Invalid Token."
            response['status'] = status.HTTP_401_UNAUTHORIZED
            raise exceptions.AuthenticationFailed(response)
    
        return self.auth_credentials(token)

    def auth_credentials(self, token):
        return(token.user, token)
# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import BlacklistedAccessToken

class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token.get("jti")

        if jti and BlacklistedAccessToken.objects.filter(jti=jti).exists():
            raise AuthenticationFailed("This access token has been blacklisted.")
        
        return token

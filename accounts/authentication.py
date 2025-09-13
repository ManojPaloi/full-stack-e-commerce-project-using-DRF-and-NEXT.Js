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

    def authenticate(self, request):
        """
        Only try to authenticate if Authorization header exists.
        Otherwise return None (DRF will treat as unauthenticated).
        """
        header = self.get_header(request)
        if header is None:
            return None  # <- prevents 'NoneType has no split' error
        raw_token = self.get_raw_token(header)
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

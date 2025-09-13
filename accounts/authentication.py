# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from .models import BlacklistedAccessToken

class CustomJWTAuthentication(JWTAuthentication):
    """
    Extends JWTAuthentication to:
    1. Block blacklisted access tokens.
    2. Automatically refresh access tokens if expired and refresh token is valid.
    """
    def authenticate(self, request):
        header = self.get_header(request)
        raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except TokenError as e:
            # If access token expired, try refreshing automatically
            refresh_token = request.COOKIES.get("refresh")
            if not refresh_token:
                raise AuthenticationFailed("Access token expired and no refresh token found.")

            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                
                # Optionally rotate refresh token
                if getattr(refresh, "blacklist", None):
                    refresh.blacklist()  # blacklist old refresh token if rotation is enabled
                new_refresh_token = str(refresh) if getattr(refresh, "blacklist", None) else refresh_token

                # Attach new tokens to request so frontend can read them from response headers
                request.META["NEW_ACCESS_TOKEN"] = new_access_token
                request.META["NEW_REFRESH_TOKEN"] = new_refresh_token

                # Validate the new access token for this request
                validated_token = self.get_validated_token(new_access_token)
            except TokenError:
                raise AuthenticationFailed("Refresh token is invalid or expired.")

        # Check if access token is blacklisted
        jti = validated_token.get("jti")
        if jti and BlacklistedAccessToken.objects.filter(jti=jti).exists():
            raise AuthenticationFailed("This access token has been blacklisted.")

        user = self.get_user(validated_token)
        return (user, validated_token)

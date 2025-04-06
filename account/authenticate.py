from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        print("called JWTCookieAuthentication")
        raw_token = (
            request.COOKIES.get(settings.SIMPLE_JWT["ACCESS_TOKEN_NAME"]) or None
        )

        print("raw_token : ", raw_token)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

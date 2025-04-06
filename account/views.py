from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Account
from .schemas import user_list_docs
from .serializers import (
    AccountSerializer,
    CustomTokenObtainPairSerializer,
    JWTCookieTokenRefreshSerializer,
    RegisterSerializer,
)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]

            forbidden_usernames = ["admin", "root", "superuser"]
            if username is forbidden_usernames:
                return Response(
                    {"error": "Username not allowed"}, status=status.HTTP_409_CONFLICT
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        errors = serializer.errors
        if "username" in errors and "non_field_errors" not in errors:
            return Response(
                {"error": "Username already exists"}, status=status.HTTP_409_CONFLICT
            )

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class LogOutAPIView(APIView):
    def post(self, request, format=None):
        response = Response("Logged out successfully")

        response.set_cookie("refresh_token", "", expires=0)
        response.set_cookie("access_token", "", expires=0)

        return response


class AccountViewSet(viewsets.ViewSet):
    queryset = Account.objects.all()
    permission_classes = [IsAuthenticated]

    # def initial(self, request, *args, **kwargs):
    #     # 요청 헤더에서 Authorization 확인
    #     auth_header = request.headers.get("Authorization", "No Authorization Header")

    #     print(
    #         "Before permission check - request.user.is_authenticated:",
    #         request.user.is_authenticated,
    #     )
    #     print("Authorization Header:", auth_header)

    #     super().initial(request, *args, **kwargs)  # 부모 클래스 실행

    @user_list_docs
    def list(self, request):
        user_id = request.query_params.get("user_id")
        queryset = Account.objects.get(id=user_id)
        serializer = AccountSerializer(queryset)
        return Response(serializer.data)


class JWTSetCookieMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            response.set_cookie(
                settings.SIMPLE_JWT["REFRESH_TOKEN_NAME"],
                response.data["refresh"],
                max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                httponly=False,
                # samesite=settings.SIMPLE_JWT["JWT_COOKIE_SAMESITE"],
                samesite="None",  # 크로스 도메인 요청 가능
                secure=True,  # HTTPS 환경 필수
            )
        if response.data.get("access"):
            response.set_cookie(
                settings.SIMPLE_JWT["ACCESS_TOKEN_NAME"],
                response.data["access"],
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                httponly=False,
                # samesite=settings.SIMPLE_JWT["JWT_COOKIE_SAMESITE"],
                samesite="None",  # 크로스 도메인 요청 가능
                secure=True,  # HTTPS 환경 필수
            )
            # del response.data["access"]
        print("쿠키 결과 : ", response.cookies)
        return super().finalize_response(request, response, *args, **kwargs)


class JWTCookieTokenObtainPairView(JWTSetCookieMixin, TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class JWTCookieTokenRefreshView(JWTSetCookieMixin, TokenRefreshView):
    serializer_class = JWTCookieTokenRefreshSerializer

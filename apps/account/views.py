import logging
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.account.services import AccountService

from .serializers import (
    BankAccountSerializer,
    UserRegistrationResponseSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(
    request=UserRegistrationSerializer,
    responses={201: UserRegistrationResponseSerializer},
    tags=["auth"],
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"User successfully registered: {user.email}")

        return Response(
            {
                "user": UserSerializer(user).data,
                "account": BankAccountSerializer(user.bank_account).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            if email := request.data.get("email"):
                AccountService.update_last_login(email)
                logger.info(f"Login successful, updating last_login for: {email}")
        return response

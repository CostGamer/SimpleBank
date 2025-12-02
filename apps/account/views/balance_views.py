import logging
from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.models import User

from ..serializers import (
    BalanceSerializer,
)

logger = logging.getLogger(__name__)


class BalanceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: BalanceSerializer}, tags=["Account"])
    def get(self, request: Request) -> Response:
        user = cast(User, request.user)

        logger.info(f"Balance request from user: {user.email}")
        bank_account = user.bank_account

        serializer = BalanceSerializer(
            {
                "account_number": bank_account.account_number,
                "balance": bank_account.balance,
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

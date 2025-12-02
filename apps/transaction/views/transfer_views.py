import logging
from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.models import User

from ..serializers import TransferResponseSerializer, TransferSerializer
from ..services import TransactionService

logger = logging.getLogger(__name__)


class TransferView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransferSerializer

    @extend_schema(
        tags=["Transactions"],
        request=TransferSerializer,
        responses={
            200: TransferResponseSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="Transfer money to another account",
        description=(
            "Transfer money from authenticated user's account to another account. "
            "A transfer fee of 2.5% (minimum €5) will be applied."
        ),
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        user = cast(User, request.user)

        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        to_account = serializer.validated_data["to_account_number"]
        amount = serializer.validated_data["amount"]
        transaction_id = serializer.validated_data.get("transaction_id")

        logger.info(
            f"Transfer request from user {user.email}: "
            f"to={to_account}, amount=€{amount}"
        )

        try:
            result = TransactionService.execute_transfer(
                sender_account=user.bank_account,
                to_account_number=to_account,
                amount=amount,
                transaction_id=transaction_id,
            )

            logger.info(
                f"Transfer successful: operation_id={result['operation_id']}, "
                f"user={user.email}"
            )

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.warning(f"Transfer failed for user {user.email}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(
                f"Unexpected error during transfer for user {user.email}: {str(e)}",
                exc_info=True,
            )
            return Response(
                {"error": "Transfer failed. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

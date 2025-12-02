import logging
from typing import cast

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.account.models import User

from ..filters import TransactionFilter
from ..models import Transaction
from ..serializers import TransactionSerializer

logger = logging.getLogger(__name__)


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter

    @extend_schema(
        tags=["Transactions"],
        parameters=[
            OpenApiParameter(
                name="from_date",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description="Filter transactions from this date (optional)",
                required=False,
            ),
            OpenApiParameter(
                name="to_date",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description="Filter transactions to this date (optional)",
                required=False,
            ),
            OpenApiParameter(
                name="transaction_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by transaction type: credit, debit, bonus (optional)",
                required=False,
                enum=["credit", "debit", "bonus"],
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number (optional, default: 1)",
                required=False,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = cast(User, self.request.user)
        logger.info(f"Transaction list request from user: {user.email}")
        return Transaction.objects.filter(account=user.bank_account)

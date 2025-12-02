from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination

from .models import Transaction


class TransactionFilter(filters.FilterSet):
    from_date = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    to_date = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    transaction_type = filters.ChoiceFilter(
        choices=Transaction.TRANSACTION_TYPE_CHOICES
    )

    class Meta:
        model = Transaction
        fields = ["from_date", "to_date", "transaction_type"]


class TransactionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100

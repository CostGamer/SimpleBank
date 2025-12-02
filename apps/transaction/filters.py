from django_filters import rest_framework as filters

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

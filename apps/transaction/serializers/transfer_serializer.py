from decimal import Decimal

from rest_framework import serializers


class TransferSerializer(serializers.Serializer):
    to_account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
    transaction_id = serializers.UUIDField(required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class TransferResponseSerializer(serializers.Serializer):
    operation_id = serializers.CharField()
    sender_transaction_id = serializers.CharField()
    receiver_transaction_id = serializers.CharField()
    fee_transaction_id = serializers.CharField()
    amount = serializers.CharField()
    fee = serializers.CharField()
    total_debited = serializers.CharField()
    sender_balance_before = serializers.CharField()
    sender_balance_after = serializers.CharField()

from rest_framework import serializers


class BalanceSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)

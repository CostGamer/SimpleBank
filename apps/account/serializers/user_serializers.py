from rest_framework import serializers

from ..models import BankAccount, User
from ..services import AccountService


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def create(self, validated_data: dict) -> User:
        result = AccountService.create_user_with_account(
            email=validated_data["email"], password=validated_data["password"]
        )
        return result["user"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ["account_number", "balance", "created_at"]
        read_only_fields = ["account_number", "balance", "created_at"]


class UserRegistrationResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    account = BankAccountSerializer()

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import User
from apps.transaction.models import Transaction


@pytest.mark.django_db
class TestRegistration:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/auth/sign_up/"

    def test_successful_registration(self):
        data = {"email": "newuser@test.com", "password": "testpass123"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert "account" in response.data
        assert response.data["user"]["email"] == "newuser@test.com"

        assert User.objects.filter(email="newuser@test.com").exists()

        user = User.objects.get(email="newuser@test.com")
        assert hasattr(user, "bank_account")
        assert user.bank_account.balance == Decimal("10000.00")

        assert Transaction.objects.filter(
            account=user.bank_account, transaction_type=Transaction.BONUS
        ).exists()

    def test_registration_duplicate_email(self):
        User.objects.create_user(email="existing@test.com", password="pass123")

        data = {"email": "existing@test.com", "password": "newpass123"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_registration_invalid_email(self):
        data = {"email": "not-an-email", "password": "testpass123"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_registration_short_password(self):
        data = {"email": "user@test.com", "password": "short"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_registration_missing_fields(self):
        data = {"email": "user@test.com"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_account_number_generated(self):
        data = {"email": "user1@test.com", "password": "testpass123"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        account_number = response.data["account"]["account_number"]
        assert len(account_number) == 10
        assert account_number.isdigit()

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestTransfer:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/transactions/transfer"

        self.sender_email = "sender@test.com"
        self.sender_password = "testpass123"
        self.receiver_email = "receiver@test.com"
        self.receiver_password = "testpass123"

        sender_response = self.client.post(
            "/api/auth/sign_up/",
            {"email": self.sender_email, "password": self.sender_password},
            format="json",
        )
        assert sender_response.status_code == 201

        receiver_response = self.client.post(
            "/api/auth/sign_up/",
            {"email": self.receiver_email, "password": self.receiver_password},
            format="json",
        )
        assert receiver_response.status_code == 201

        self.receiver_account_number = receiver_response.data["account"][
            "account_number"
        ]

    def _get_auth_token(self, email=None, password=None):
        email = email or self.sender_email
        password = password or self.sender_password

        response = self.client.post(
            "/api/auth/login/", {"email": email, "password": password}, format="json"
        )
        return response.data["access"]

    def test_successful_transfer(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"to_account_number": self.receiver_account_number, "amount": "100.00"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "operation_id" in response.data
        assert "sender_transaction_id" in response.data
        assert "receiver_transaction_id" in response.data
        assert "fee_transaction_id" in response.data
        assert response.data["amount"] == "100.00"
        assert response.data["fee"] == "5.00"
        assert response.data["total_debited"] == "105.00"

    def test_transfer_with_calculated_fee(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"to_account_number": self.receiver_account_number, "amount": "1000.00"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == "1000.00"
        assert response.data["fee"] == "25.00"
        assert response.data["total_debited"] == "1025.00"

    def test_transfer_insufficient_funds(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "to_account_number": self.receiver_account_number,
            "amount": "999999.00",
        }

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Insufficient funds" in response.data["error"]

    def test_transfer_to_nonexistent_account(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"to_account_number": "9999999999", "amount": "100.00"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "not found" in response.data["error"]

    def test_transfer_to_yourself(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        balance_response = self.client.get("/api/auth/balance/")
        my_account_number = balance_response.data["account_number"]

        data = {"to_account_number": my_account_number, "amount": "100.00"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "yourself" in response.data["error"].lower()

    def test_transfer_negative_amount(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"to_account_number": self.receiver_account_number, "amount": "-100.00"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_transfer_zero_amount(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"to_account_number": self.receiver_account_number, "amount": "0.00"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_transfer_unauthenticated(self):
        data = {"to_account_number": self.receiver_account_number, "amount": "100.00"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_transfer_idempotency(self):
        import uuid

        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        transaction_id = str(uuid.uuid4())

        data = {
            "to_account_number": self.receiver_account_number,
            "amount": "100.00",
            "transaction_id": transaction_id,
        }

        response1 = self.client.post(self.url, data, format="json")
        assert response1.status_code == status.HTTP_200_OK

        response2 = self.client.post(self.url, data, format="json")
        assert response2.status_code == status.HTTP_200_OK

        assert response1.data["operation_id"] == response2.data["operation_id"]
        assert response1.data["amount"] == response2.data["amount"]

    def test_transfer_updates_balance(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        balance_before = self.client.get("/api/auth/balance/").data["balance"]

        data = {"to_account_number": self.receiver_account_number, "amount": "100.00"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

        balance_after = self.client.get("/api/auth/balance/").data["balance"]

        expected_balance = Decimal(balance_before) - Decimal("105.00")  # 100 + 5 fee
        assert Decimal(balance_after) == expected_balance

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestBalance:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/auth/balance/"
        self.user_email = "testuser@test.com"
        self.user_password = "testpass123"

        self._register_user()

    def _register_user(self):
        response = self.client.post(
            "/api/auth/sign_up/",
            {"email": self.user_email, "password": self.user_password},
            format="json",
        )
        assert response.status_code == 201
        self.account_number = response.data["account"]["account_number"]

    def _get_auth_token(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.user_email, "password": self.user_password},
            format="json",
        )
        return response.data["access"]

    def test_get_balance_authenticated(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["balance"] == "10000.00"
        assert response.data["account_number"] == self.account_number

    def test_get_balance_unauthenticated(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_balance_format(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.url)

        balance = response.data["balance"]
        assert isinstance(balance, str)
        assert "." in balance
        assert len(balance.split(".")[1]) == 2

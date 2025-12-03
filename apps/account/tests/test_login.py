import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import User


@pytest.mark.django_db
class TestLogin:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/auth/login/"

        self.user = User.objects.create_user(
            email="testuser@test.com", password="testpass123"
        )

    def test_successful_login(self):
        data = {"email": "testuser@test.com", "password": "testpass123"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

        assert isinstance(response.data["access"], str)
        assert isinstance(response.data["refresh"], str)

    def test_login_wrong_password(self):
        data = {"email": "testuser@test.com", "password": "wrongpassword"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self):
        data = {"email": "nonexistent@test.com", "password": "testpass123"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_email(self):
        data = {"password": "testpass123"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_password(self):
        data = {"email": "testuser@test.com"}

        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

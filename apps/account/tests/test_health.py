import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestHealthCheck:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/auth/health/"

    def test_health_check_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ok"
        assert response.data["database"] == "connected"
        assert "version" in response.data

    def test_health_check_no_authentication_required(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

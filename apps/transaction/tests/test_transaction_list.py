from datetime import datetime, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestTransactionList:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/transactions/"

        self.user_email = "testuser@test.com"
        self.user_password = "testpass123"
        self.receiver_email = "receiver@test.com"
        self.receiver_password = "testpass123"

        register_response = self.client.post(
            "/api/auth/sign_up/",
            {"email": self.user_email, "password": self.user_password},
            format="json",
        )
        assert register_response.status_code == 201

        self.account_number = register_response.data["account"]["account_number"]

        receiver_response = self.client.post(
            "/api/auth/sign_up/",
            {"email": self.receiver_email, "password": self.receiver_password},
            format="json",
        )
        assert receiver_response.status_code == 201
        self.receiver_account_number = receiver_response.data["account"][
            "account_number"
        ]

        self._create_test_transfers()

        self.client.credentials()

    def _get_auth_token(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.user_email, "password": self.user_password},
            format="json",
        )
        return response.data["access"]

    def _create_test_transfers(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        transfer_amounts = ["100.00", "200.00", "50.00", "150.00", "75.00"]

        for amount in transfer_amounts:
            response = self.client.post(
                "/api/transactions/transfer",
                {"to_account_number": self.receiver_account_number, "amount": amount},
                format="json",
            )
            assert response.status_code == status.HTTP_200_OK

    def test_get_transactions_authenticated(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data

        assert response.data["count"] == 6

        first_transaction = response.data["results"][0]
        assert "transaction_id" in first_transaction
        assert "amount" in first_transaction
        assert "transaction_type" in first_transaction
        assert "description" in first_transaction
        assert "created_at" in first_transaction
        assert "metadata" in first_transaction

    def test_get_transactions_unauthenticated(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_transactions_pagination_limit(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.url, {"limit": "3"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
        assert response.data["count"] == 6
        assert response.data["next"] is not None

    def test_transactions_pagination_pages(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response_page1 = self.client.get(self.url, {"limit": "2", "page": "1"})
        assert response_page1.status_code == status.HTTP_200_OK
        assert len(response_page1.data["results"]) == 2

        response_page2 = self.client.get(self.url, {"limit": "2", "page": "2"})
        assert response_page2.status_code == status.HTTP_200_OK
        assert len(response_page2.data["results"]) == 2

        page1_ids = [t["transaction_id"] for t in response_page1.data["results"]]
        page2_ids = [t["transaction_id"] for t in response_page2.data["results"]]
        assert set(page1_ids).isdisjoint(set(page2_ids))

    def test_transactions_filter_by_type_bonus(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.url, {"transaction_type": "bonus"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        for transaction in response.data["results"]:
            assert transaction["transaction_type"] == "bonus"

    def test_transactions_filter_by_date_range(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        to_date = datetime.now()
        from_date = to_date - timedelta(days=7)

        response = self.client.get(
            self.url,
            {"from_date": from_date.isoformat(), "to_date": to_date.isoformat()},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 6

    def test_transactions_filter_future_date(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        future_date = datetime.now() + timedelta(days=30)

        response = self.client.get(self.url, {"from_date": future_date.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_transactions_filter_past_date(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        past_date = datetime.now() - timedelta(days=30)

        response = self.client.get(self.url, {"from_date": past_date.isoformat()})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 6

    def test_transactions_combined_filters(self):
        token = self._get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        from_date = datetime.now() - timedelta(days=1)

        response = self.client.get(
            self.url,
            {
                "transaction_type": "debit",
                "from_date": from_date.isoformat(),
                "limit": "2",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        for transaction in response.data["results"]:
            assert transaction["transaction_type"] == "debit"

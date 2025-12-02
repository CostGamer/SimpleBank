import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.transaction.models import Transaction

from .models import BankAccount, User

logger = logging.getLogger(__name__)


class AccountService:
    WELCOME_BONUS = Decimal("10000.00")

    @staticmethod
    @transaction.atomic
    def create_user_with_account(email: str, password: str) -> dict[str, Any]:
        """Создаёт пользователя, счёт и начисляет welcome бонус"""
        user = User.objects.create_user(email=email, password=password)
        bank_account = BankAccount.objects.create(user=user)

        Transaction.objects.create(
            account=bank_account,
            amount=AccountService.WELCOME_BONUS,
            transaction_type=Transaction.BONUS,
            description="Welcome bonus",
        )

        logger.info(f"User created with bonus: {email}")
        return {"user": user, "account": bank_account}

    @staticmethod
    def update_last_login(email: str) -> None:
        user: User | None = User.objects.filter(email=email).first()
        if user:
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.transaction.models import Transaction

from .models import BankAccount, User

logger = logging.getLogger(__name__)


class AccountService:
    WELCOME_BONUS = Decimal("10000.00")

    @staticmethod
    @transaction.atomic
    def create_user_with_account(email: str, password: str) -> dict[str, Any]:
        user = User.objects.create_user(email=email, password=password)
        bank_account = BankAccount.objects.create(user=user)

        BankAccount.objects.filter(pk=bank_account.pk).update(
            balance=F("balance") + AccountService.WELCOME_BONUS
        )

        Transaction.objects.create(
            account=bank_account,
            amount=AccountService.WELCOME_BONUS,
            transaction_type=Transaction.BONUS,
            description="Welcome bonus",
        )

        bank_account.refresh_from_db()

        logger.info(
            f"User created with bonus: {email}, "
            f"account: {bank_account.account_number}, "
        )

        return {
            "user": user,
            "account": bank_account,
        }

    @staticmethod
    def update_last_login(email: str) -> None:
        User.objects.filter(email=email).update(last_login=timezone.now())

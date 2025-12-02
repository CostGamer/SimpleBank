import uuid
from typing import Any

from django.db import models

from apps.account.models import BankAccount


class Transaction(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"
    BONUS = "bonus"

    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
        (BONUS, "Bonus"),
    ]

    account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.transaction_type} {self.amount} - {self.account.account_number}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            if self.transaction_type in [self.CREDIT, self.BONUS]:
                self.account.balance += self.amount
            elif self.transaction_type == self.DEBIT:
                self.account.balance -= self.amount

            self.account.save()

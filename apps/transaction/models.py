import uuid

from django.db import models

from apps.account.models import BankAccount


class Transaction(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"
    BONUS = "bonus"
    FEE = "fee"

    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
        (BONUS, "Bonus"),
        (FEE, "Fee"),
    ]

    account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.UUIDField(unique=True, default=uuid.uuid4)
    metadata = models.JSONField(null=True, blank=True, default=dict)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.transaction_type} {self.amount} - {self.account.account_number}"

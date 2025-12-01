from django.db import models

from apps.account.models import BankAccount


class Transaction(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"

    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
    ]

    account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.transaction_type} {self.amount} - {self.account.account_number}"

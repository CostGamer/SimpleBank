import logging
import uuid
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import F

from apps.account.models import BankAccount

from .models import Transaction

logger = logging.getLogger(__name__)


class TransactionService:
    FEE_PERCENTAGE = Decimal("0.025")  # 2.5%
    MIN_FEE = Decimal("5.00")  # €5

    @staticmethod
    def calculate_fee(amount: Decimal) -> Decimal:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        fee = amount * TransactionService.FEE_PERCENTAGE
        return Decimal(max(fee, TransactionService.MIN_FEE))

    @staticmethod
    @transaction.atomic
    def execute_transfer(
        sender_account: BankAccount,
        to_account_number: str,
        amount: Decimal,
        transaction_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        transfer_operation_id = transaction_id or uuid.uuid4()

        if existing_txn := Transaction.objects.filter(
            transaction_id=transfer_operation_id
        ).first():
            logger.warning(f"Duplicate transaction attempt: {transfer_operation_id}")

            assert existing_txn.metadata is not None

            receiver_transaction_id = existing_txn.metadata.get("receiver_txn_id")
            fee_transaction_id = existing_txn.metadata.get("fee_txn_id")
            fee_txn = existing_txn.metadata.get("fee")
            total_debit = existing_txn.metadata.get("total_debited")
            sender_balance_before = existing_txn.metadata.get("balance_before")
            sender_balance_after = existing_txn.metadata.get("balance_after")
            transfer_amount = existing_txn.metadata.get("transfer_amount")
            transfer_fee = existing_txn.metadata.get("fee")

            return {
                "operation_id": str(transfer_operation_id),
                "sender_transaction_id": str(transfer_operation_id),
                "receiver_transaction_id": str(receiver_transaction_id),
                "fee_transaction_id": str(fee_transaction_id),
                "amount": str(transfer_amount),
                "fee": str(transfer_fee),
                "total_debited": str(total_debit),
                "sender_balance_before": str(sender_balance_before),
                "sender_balance_after": str(sender_balance_after),
            }

        try:
            receiver_account = BankAccount.objects.get(account_number=to_account_number)
        except BankAccount.DoesNotExist as e:
            raise ValueError(f"Account {to_account_number} not found") from e

        if sender_account.pk == receiver_account.pk:
            raise ValueError("Cannot transfer to yourself")

        # Lock accounts
        locked_accounts = list(
            BankAccount.objects.select_for_update()
            .filter(pk__in=[sender_account.pk, receiver_account.pk])
            .order_by("pk")
        )
        locked_map = {acc.pk: acc for acc in locked_accounts}
        sender_locked = locked_map[sender_account.pk]
        receiver_locked = locked_map[receiver_account.pk]

        # Calculate amounts
        fee = TransactionService.calculate_fee(amount)
        total_debit = amount + fee

        if sender_locked.balance < total_debit:
            raise ValueError(
                f"Insufficient funds. Required: €{total_debit}, "
                f"Available: €{sender_locked.balance}"
            )

        system_account = BankAccount.get_system_account()

        # Save balances BEFORE changes
        sender_balance_before = sender_locked.balance
        receiver_balance_before = receiver_locked.balance
        system_balance_before = system_account.balance

        BankAccount.objects.filter(pk=sender_locked.pk).update(
            balance=F("balance") - total_debit
        )
        BankAccount.objects.filter(pk=receiver_locked.pk).update(
            balance=F("balance") + amount
        )
        BankAccount.objects.filter(pk=system_account.pk).update(
            balance=F("balance") + fee
        )

        sender_locked.refresh_from_db()
        receiver_locked.refresh_from_db()
        system_account.refresh_from_db()

        receiver_txn_id = uuid.uuid4()
        fee_txn_id = uuid.uuid4()

        # Create transactions with metadata including balance snapshots
        sender_txn = Transaction.objects.create(
            transaction_id=transfer_operation_id,
            account=sender_locked,
            amount=total_debit,
            transaction_type=Transaction.DEBIT,
            description=f"Transfer to {to_account_number}",
            metadata={
                "operation": "transfer",
                "operation_id": str(transfer_operation_id),
                "receiver_txn_id": str(receiver_txn_id),
                "fee_txn_id": str(fee_txn_id),
                "role": "sender",
                "counterparty_account": to_account_number,
                "transfer_amount": str(amount),
                "fee": str(fee),
                "total_debited": str(Decimal(total_debit)),
                "balance_before": str(sender_balance_before),
                "balance_after": str(sender_locked.balance),
            },
        )

        receiver_txn = Transaction.objects.create(
            transaction_id=receiver_txn_id,
            account=receiver_locked,
            amount=amount,
            transaction_type=Transaction.CREDIT,
            description=f"Transfer from {sender_locked.account_number}",
            metadata={
                "operation": "transfer",
                "operation_id": str(transfer_operation_id),
                "receiver_txn_id": str(receiver_txn_id),
                "fee_txn_id": str(fee_txn_id),
                "role": "receiver",
                "counterparty_account": sender_locked.account_number,
                "transfer_amount": str(amount),
                "balance_before": str(receiver_balance_before),
                "balance_after": str(receiver_locked.balance),
            },
        )

        fee_txn = Transaction.objects.create(
            transaction_id=fee_txn_id,
            account=system_account,
            amount=fee,
            transaction_type=Transaction.FEE,
            description=f"Transfer fee: {sender_locked.account_number} to {to_account_number}",
            metadata={
                "operation": "transfer",
                "operation_id": str(transfer_operation_id),
                "receiver_txn_id": str(receiver_txn_id),
                "fee_txn_id": str(fee_txn_id),
                "role": "fee",
                "sender_account": sender_locked.account_number,
                "receiver_account": to_account_number,
                "transfer_amount": str(amount),
                "balance_before": str(system_balance_before),
                "balance_after": str(system_account.balance),
            },
        )

        logger.info(
            f"Transfer completed: {sender_locked.account_number} → {to_account_number}, "
            f"amount: €{amount}, fee: €{fee}, operation_id: {transfer_operation_id}"
        )

        return {
            "operation_id": str(transfer_operation_id),
            "sender_transaction_id": str(sender_txn.transaction_id),
            "receiver_transaction_id": str(receiver_txn.transaction_id),
            "fee_transaction_id": str(fee_txn.transaction_id),
            "amount": str(amount),
            "fee": str(fee),
            "total_debited": str(total_debit),
            "sender_balance_before": str(sender_balance_before),
            "sender_balance_after": str(sender_locked.balance),
        }

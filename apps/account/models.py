import random
from typing import Any, ClassVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager[Any]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> Any:
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user: User = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None  # type: ignore[assignment]
    email = models.EmailField(unique=True)

    objects: ClassVar[UserManager] = UserManager()  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email


class BankAccount(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="bank_account"
    )
    account_number = models.CharField(max_length=10, unique=True, editable=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bank_accounts"

    def __str__(self) -> str:
        return f"{self.account_number} - {self.user.email}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.account_number:
            self.account_number = self._generate_account_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_account_number() -> str:
        while True:
            number = "".join([str(random.randint(0, 9)) for _ in range(10)])
            if not BankAccount.objects.filter(account_number=number).exists():
                return number

    @staticmethod
    def get_system_account() -> "BankAccount":
        try:
            system_user = User.objects.get(email="system@simplebank.internal")
            return system_user.bank_account
        except User.DoesNotExist:
            raise ValueError("System account not found. Run migrations") from None

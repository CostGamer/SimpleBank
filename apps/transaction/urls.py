from django.urls import path

from .views import TransactionListView, TransferView

urlpatterns = [
    path("", TransactionListView.as_view(), name="transaction_list"),
    path("transfer", TransferView.as_view(), name="transfer"),
]

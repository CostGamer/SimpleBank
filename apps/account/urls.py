from django.urls import path

from .views import BalanceView, LoginView, RegisterView

urlpatterns = [
    path("sign_up/", RegisterView.as_view(), name="sign_up"),
    path("login/", LoginView.as_view(), name="login"),
    path("balance/", BalanceView.as_view(), name="balance"),
]

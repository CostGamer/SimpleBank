import logging

from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        health_status = {
            "status": "ok",
            "version": "1.0.0",
            "database": self._check_database(),
        }

        if health_status["database"] == "disconnected":
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_status, status=status.HTTP_200_OK)

    def _check_database(self) -> str:
        try:
            connection.ensure_connection()
            return "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return "disconnected"

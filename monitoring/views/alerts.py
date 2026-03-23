from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from monitoring.models import Alert
from monitoring.serializers.alerts import AlertSerializer


class AlertViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Alert.objects.all().order_by("-created_at")
    serializer_class = AlertSerializer
    ordering_fields = ["created_at", "severity"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["severity", "is_active"]

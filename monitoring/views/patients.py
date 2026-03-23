from datetime import timedelta

from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from monitoring.models import Alert, AlertSeverity, Patient
from monitoring.serializers.observations import ObservationSerializer
from monitoring.serializers.patients import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer
    http_method_names = ["get", "post", "patch"]
    search_fields = ["first_name", "last_name", "mrn"]

    @action(detail=False, methods=["get"], url_path="high-risk")
    def high_risk(self, request):
        threshold = timezone.now() - timedelta(hours=24)

        recent_severe_alerts = Alert.objects.filter(
            patient_id=OuterRef("pk"),
            is_active=True,
            severity=AlertSeverity.SEVERE,
            created_at__gte=threshold,
        )

        queryset = (
            Patient.objects.annotate(is_high_risk=Exists(recent_severe_alerts))
            .filter(is_high_risk=True)
            .order_by("-created_at")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="observations")
    def observations(self, request, pk=None):
        patient = self.get_object()
        queryset = patient.observations.all().order_by("-recorded_at")

        page = self.paginate_queryset(queryset)
        serializer = ObservationSerializer(page or queryset, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

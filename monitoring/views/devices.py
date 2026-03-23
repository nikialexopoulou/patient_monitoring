from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from monitoring.models import Device, Patient
from monitoring.serializers.devices import (
    AssignDeviceSerializer,
    DeviceDetailSerializer,
    DeviceSerializer,
)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().order_by("-assigned_at")
    serializer_class = DeviceSerializer
    http_method_names = ["post"]

    @extend_schema(
        request=AssignDeviceSerializer,
        responses={200: DeviceDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="assign")
    @transaction.atomic
    def assign(self, request, pk=None):
        device = Device.objects.select_for_update().filter(pk=pk).first()

        if not device:
            return Response(
                {"error": "Device does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if device.assigned_patient is not None:
            return Response(
                {"error": "Device is already assigned to another patient."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = AssignDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = Patient.objects.filter(id=serializer.validated_data["patient_id"]).first()

        if not patient:
            return Response(
                {"error": "Patient does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        device.assigned_patient = patient
        device.assigned_at = timezone.now()
        device.save(update_fields=["assigned_patient", "assigned_at"])

        return Response(DeviceDetailSerializer(device).data, status=status.HTTP_200_OK)

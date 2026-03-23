from rest_framework import serializers

from monitoring.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        read_only_fields = ("id", "assigned_at")


class AssignDeviceSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()


class DeviceDetailSerializer(serializers.ModelSerializer):
    patient_id = serializers.UUIDField(source="assigned_patient.id", read_only=True)

    class Meta:
        model = Device
        fields = [
            "id",
            "serial_number",
            "model",
            "assigned_patient",
            "patient_id",
            "assigned_at",
        ]

from django.utils import timezone
from rest_framework import serializers

from monitoring.models import Observation, Patient


class ObservationSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        error_messages={
            "does_not_exist": "Patient does not exist.",
            "incorrect_type": "Invalid patient ID.",
        },
    )

    class Meta:
        model = Observation
        fields = "__all__"

    def validate_heart_rate(self, value):
        if value is not None and not 20 <= value <= 300:
            raise serializers.ValidationError("Heart rate must be between 20 and 300 bpm.")
        return value

    def validate_respiratory_rate(self, value):
        if value is not None and not 5 <= value <= 80:
            raise serializers.ValidationError(
                "Respiratory rate must be between 5 and 80 breaths/min."
            )
        return value

    def validate_temperature(self, value):
        if value is not None and not 25 <= value <= 45:
            raise serializers.ValidationError("Temperature must be between 25 and 45 °C.")
        return value

    def validate_spo2(self, value):
        if value is not None and not 0 <= value <= 100:
            raise serializers.ValidationError("SpO2 must be between 0 and 100 percent.")
        return value

    def validate_systolic_bp(self, value):
        if value is not None and not 40 <= value <= 300:
            raise serializers.ValidationError(
                "Systolic blood pressure must be between 40 and 300 mmHg."
            )
        return value

    def validate_recorded_at(self, value):
        now = timezone.now()
        if value > now:
            raise serializers.ValidationError("Recorded time cannot be in the future.")

        return value


class ObservationQuerySerializer(serializers.Serializer):
    from_ = serializers.DateTimeField(required=False, source="from")
    to = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        from_dt = attrs.get("from")
        to_dt = attrs.get("to")

        if from_dt and to_dt and from_dt > to_dt:
            raise serializers.ValidationError(
                {"detail": "'from' must be earlier than or equal to 'to'."}
            )

        return attrs

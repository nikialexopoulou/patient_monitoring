from rest_framework import serializers

from monitoring.models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate_date_of_birth(self, value):
        from django.utils import timezone

        if value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

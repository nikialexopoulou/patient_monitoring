import uuid

from django.db import models
from django.db.models import Q


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    mrn = models.CharField(max_length=50, unique=True, db_index=True)
    is_high_priority = models.BooleanField(default=False)
    spi_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patients"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["last_name", "first_name"]),
        ]


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial_number = models.CharField(max_length=100, unique=True, db_index=True)
    model = models.CharField(max_length=100)
    assigned_patient = models.ForeignKey(
        "Patient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
    )
    assigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "devices"
        constraints = [
            models.CheckConstraint(
                condition=Q(assigned_patient__isnull=True, assigned_at__isnull=True)
                | Q(assigned_patient__isnull=False, assigned_at__isnull=False),
                name="device_assignment_timestamp_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["assigned_at"]),
        ]


class Observation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="observations",
    )
    recorded_at = models.DateTimeField()
    heart_rate = models.IntegerField(null=True, blank=True)
    respiratory_rate = models.IntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    spo2 = models.IntegerField(null=True, blank=True)
    systolic_bp = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "observations"
        constraints = [
            models.CheckConstraint(
                condition=(Q(heart_rate__gte=20) & Q(heart_rate__lte=300))
                | Q(heart_rate__isnull=True),
                name="heart_rate_valid_range",
            ),
            models.CheckConstraint(
                condition=(Q(respiratory_rate__gte=5) & Q(respiratory_rate__lte=80))
                | Q(respiratory_rate__isnull=True),
                name="respiratory_rate_valid_range",
            ),
            models.CheckConstraint(
                condition=(Q(temperature__gte=25) & Q(temperature__lte=45))
                | Q(temperature__isnull=True),
                name="temperature_valid_range",
            ),
            models.CheckConstraint(
                condition=(Q(spo2__gte=0) & Q(spo2__lte=100)) | Q(spo2__isnull=True),
                name="spo2_valid_range",
            ),
            models.CheckConstraint(
                condition=(Q(systolic_bp__gte=40) & Q(systolic_bp__lte=300))
                | Q(systolic_bp__isnull=True),
                name="systolic_bp_valid_range",
            ),
        ]
        indexes = [
            models.Index(fields=["patient", "-recorded_at"]),
            models.Index(fields=["recorded_at"]),
        ]


class AlertSeverity(models.TextChoices):
    SEVERE = "SEVERE", "Severe"
    MILD = "MILD", "Mild"


class AlertType(models.TextChoices):
    HIGH_HEART_RATE = "HIGH_HEART_RATE", "High heart rate"
    HIGH_TEMPERATURE = "HIGH_TEMPERATURE", "High temperature"
    LOW_SPO2 = "LOW_SPO2", "Low SpO2"


class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    type = models.CharField(max_length=50, choices=AlertType.choices)
    severity = models.CharField(max_length=50, choices=AlertSeverity.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "alerts"
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "type"],
                condition=Q(is_active=True),
                name="unique_active_alert_per_patient_and_type",
            ),
        ]
        indexes = [
            models.Index(fields=["patient", "is_active", "severity", "created_at"]),
            models.Index(fields=["created_at"]),
        ]

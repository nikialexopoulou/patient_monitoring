from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from monitoring.models import Alert, AlertSeverity, AlertType, Observation, Patient


@pytest.mark.django_db
def test_create_patient_success(auth_client):
    url = reverse("patients-list")

    response = auth_client.post(
        url,
        {
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "mrn": "MRN-NEW",
            "is_high_priority": True,
            "spi_enabled": True,
        },
        format="json",
    )

    assert response.status_code == 201

    patient = Patient.objects.get(mrn="MRN-NEW")
    assert patient.first_name == "Test"
    assert patient.is_high_priority is True
    assert patient.spi_enabled is True


@pytest.mark.django_db
def test_get_patients_list(auth_client, patient):
    url = reverse("patients-list")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data

    ids = {item["id"] for item in results}
    assert str(patient.id) in ids


@pytest.mark.django_db
def test_high_risk_returns_patient_with_recent_severe_alert(auth_client, patient):
    Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Severe alert",
        is_active=True,
        created_at=timezone.now() - timedelta(hours=1),
    )

    url = reverse("patients-high-risk")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(patient.id) in ids


@pytest.mark.django_db
def test_high_risk_excludes_inactive_alerts(auth_client, patient):
    Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Inactive alert",
        is_active=False,
        created_at=timezone.now(),
    )

    url = reverse("patients-high-risk")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(patient.id) not in ids


@pytest.mark.django_db
def test_high_risk_returns_only_severe_alerts(auth_client, patient):
    Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.MILD,
        message="Mild alert",
        is_active=True,
        created_at=timezone.now(),
    )

    url = reverse("patients-high-risk")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(patient.id) not in ids


@pytest.mark.django_db
def test_patient_observations_endpoint_returns_observations(auth_client, patient):
    observation = Observation.objects.create(
        patient=patient,
        recorded_at=timezone.now(),
        heart_rate=80,
    )

    url = reverse("patients-observations", kwargs={"pk": patient.id})

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(observation.id) in ids


@pytest.mark.django_db
def test_patient_observations_are_ordered_desc(auth_client, patient):
    older = Observation.objects.create(
        patient=patient,
        recorded_at=timezone.now() - timedelta(hours=2),
        heart_rate=70,
    )

    newer = Observation.objects.create(
        patient=patient,
        recorded_at=timezone.now(),
        heart_rate=90,
    )

    url = reverse("patients-observations", kwargs={"pk": patient.id})

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data

    assert results[0]["id"] == str(newer.id)
    assert results[1]["id"] == str(older.id)

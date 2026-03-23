from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from monitoring.models import Alert, AlertSeverity, AlertType, Observation


@pytest.mark.django_db
def test_create_observation_creates_alerts(auth_client, patient):
    url = reverse("observations-list")

    response = auth_client.post(
        url,
        {
            "patient": str(patient.id),
            "recorded_at": timezone.now().isoformat(),
            "heart_rate": 150,
            "temperature": "39.5",
            "spo2": 85,
        },
        format="json",
    )

    assert response.status_code == 201

    alerts = Alert.objects.filter(patient=patient, is_active=True)
    alert_types = set(alerts.values_list("type", flat=True))

    assert alerts.count() == 3
    assert "HIGH_HEART_RATE" in alert_types
    assert "HIGH_TEMPERATURE" in alert_types
    assert "LOW_SPO2" in alert_types


@pytest.mark.django_db
def test_create_observation_without_threshold_breach_creates_no_alert(auth_client, patient):
    url = reverse("observations-list")

    response = auth_client.post(
        url,
        {
            "patient": str(patient.id),
            "recorded_at": timezone.now().isoformat(),
            "heart_rate": 80,
            "temperature": "36.5",
            "spo2": 98,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Alert.objects.filter(patient=patient).count() == 0


@pytest.mark.django_db
def test_duplicate_alert_not_created_for_same_patient(auth_client, patient):
    Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Existing alert",
        is_active=True,
    )

    url = reverse("observations-list")

    response = auth_client.post(
        url,
        {
            "patient": str(patient.id),
            "recorded_at": timezone.now().isoformat(),
            "heart_rate": 140,
        },
        format="json",
    )

    assert response.status_code == 201

    alerts = Alert.objects.filter(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        is_active=True,
    )

    assert alerts.count() == 1


@pytest.mark.django_db
def test_create_observation_with_invalid_heart_rate_returns_error(auth_client, patient):
    url = reverse("observations-list")

    response = auth_client.post(
        url,
        {
            "patient": str(patient.id),
            "recorded_at": timezone.now().isoformat(),
            "heart_rate": 500,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "heart_rate" in response.json()


@pytest.mark.django_db
def test_create_observation_with_invalid_spo2_returns_error(auth_client, patient):
    url = reverse("observations-list")

    response = auth_client.post(
        url,
        {
            "patient": str(patient.id),
            "recorded_at": timezone.now().isoformat(),
            "spo2": 150,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "spo2" in response.json()


@pytest.mark.django_db
def test_create_observation_missing_fields_returns_error(auth_client):
    url = reverse("observations-list")

    response = auth_client.post(url, {}, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_observations_with_date_filter(auth_client, patient):
    old_observation = Observation.objects.create(
        patient=patient,
        recorded_at=timezone.now() - timedelta(days=2),
        heart_rate=80,
    )

    recent_observation = Observation.objects.create(
        patient=patient,
        recorded_at=timezone.now() - timedelta(hours=1),
        heart_rate=90,
    )

    url = reverse("observations-list")

    response = auth_client.get(
        url,
        {
            "from": (timezone.now() - timedelta(days=1)).isoformat(),
            "to": timezone.now().isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(recent_observation.id) in ids
    assert str(old_observation.id) not in ids


@pytest.mark.django_db
def test_list_observations_returns_paginated_results(auth_client, patient):
    for i in range(25):
        Observation.objects.create(
            patient=patient,
            recorded_at=timezone.now() - timedelta(minutes=i),
            heart_rate=70,
        )

    url = reverse("observations-list")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()

    if "results" in data:
        assert len(data["results"]) <= 20
        assert "count" in data

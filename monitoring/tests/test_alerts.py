from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from monitoring.models import Alert, AlertSeverity, AlertType


@pytest.mark.django_db
def test_list_alerts_returns_results(auth_client, patient):
    alert = Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Test alert",
        is_active=True,
    )

    url = reverse("alerts-list")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(alert.id) in ids


@pytest.mark.django_db
def test_filter_alerts_by_severity(auth_client, patient):
    severe_alert = Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Severe alert",
        is_active=True,
    )

    Alert.objects.create(
        patient=patient,
        type=AlertType.LOW_SPO2,
        severity=AlertSeverity.MILD,
        message="Mild alert",
        is_active=True,
    )

    url = reverse("alerts-list")

    response = auth_client.get(url, {"severity": "SEVERE"})

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(severe_alert.id) in ids


@pytest.mark.django_db
def test_filter_alerts_by_is_active(auth_client, patient):
    active_alert = Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Active alert",
        is_active=True,
    )

    Alert.objects.create(
        patient=patient,
        type=AlertType.LOW_SPO2,
        severity=AlertSeverity.SEVERE,
        message="Inactive alert",
        is_active=False,
    )

    url = reverse("alerts-list")

    response = auth_client.get(url, {"is_active": True})

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(active_alert.id) in ids


@pytest.mark.django_db
def test_filter_alerts_by_severity_and_is_active(auth_client, patient):
    matching_alert = Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Matching alert",
        is_active=True,
    )

    Alert.objects.create(
        patient=patient,
        type=AlertType.LOW_SPO2,
        severity=AlertSeverity.SEVERE,
        message="Inactive alert",
        is_active=False,
    )

    Alert.objects.create(
        patient=patient,
        type=AlertType.LOW_SPO2,
        severity=AlertSeverity.MILD,
        message="Wrong severity",
        is_active=True,
    )

    url = reverse("alerts-list")

    response = auth_client.get(url, {"severity": "SEVERE", "is_active": True})

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data
    ids = {item["id"] for item in results}

    assert str(matching_alert.id) in ids
    assert len(ids) == 1


@pytest.mark.django_db
def test_alerts_are_ordered_by_created_at_desc(auth_client, patient):
    older = Alert.objects.create(
        patient=patient,
        type=AlertType.HIGH_HEART_RATE,
        severity=AlertSeverity.SEVERE,
        message="Older",
        is_active=True,
        created_at=timezone.now() - timedelta(hours=2),
    )

    newer = Alert.objects.create(
        patient=patient,
        type=AlertType.LOW_SPO2,
        severity=AlertSeverity.SEVERE,
        message="Newer",
        is_active=True,
    )

    url = reverse("alerts-list")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"] if "results" in data else data

    assert results[0]["id"] == str(newer.id)
    assert results[1]["id"] == str(older.id)


@pytest.mark.django_db
def test_alerts_pagination(auth_client, patient):
    for i in range(25):
        Alert.objects.create(
            patient=patient,
            type=AlertType.HIGH_HEART_RATE,
            severity=AlertSeverity.SEVERE,
            message=f"Alert {i}",
            is_active=False,
        )

    url = reverse("alerts-list")

    response = auth_client.get(url)

    assert response.status_code == 200

    data = response.json()

    if "results" in data:
        assert len(data["results"]) <= 20
        assert "count" in data

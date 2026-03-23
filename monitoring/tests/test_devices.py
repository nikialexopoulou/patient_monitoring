import uuid
from threading import Thread

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_assign_device_success(auth_client, patient, device):
    url = reverse("devices-assign", kwargs={"pk": device.id})

    response = auth_client.post(
        url,
        {"patient_id": str(patient.id)},
        format="json",
    )

    assert response.status_code == 200

    device.refresh_from_db()
    assert device.assigned_patient == patient
    assert device.assigned_at is not None

    res = response.json()
    assert res["id"] == str(device.id)
    assert res["patient_id"] == str(patient.id)
    assert res["assigned_patient"] == str(patient.id)
    assert res["assigned_at"] is not None


@pytest.mark.django_db
def test_assign_device_already_assigned_returns_conflict(
    auth_client, patient, second_patient, device
):
    device.assigned_patient = patient
    device.assigned_at = timezone.now()
    device.save(update_fields=["assigned_patient", "assigned_at"])

    url = reverse("devices-assign", kwargs={"pk": device.id})

    response = auth_client.post(
        url,
        {"patient_id": str(second_patient.id)},
        format="json",
    )

    assert response.status_code == 409
    assert response.json() == {"error": "Device is already assigned to another patient."}

    device.refresh_from_db()
    assert device.assigned_patient == patient
    assert device.assigned_at is not None


@pytest.mark.django_db
def test_assign_device_to_nonexistent_patient_returns_not_found(auth_client, device):
    url = reverse("devices-assign", kwargs={"pk": device.id})

    response = auth_client.post(
        url,
        {"patient_id": str(uuid.uuid4())},
        format="json",
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Patient does not exist."}

    device.refresh_from_db()
    assert device.assigned_patient is None
    assert device.assigned_at is None


@pytest.mark.django_db
def test_assign_device_missing_patient_id_returns_bad_request(auth_client, device):
    url = reverse("devices-assign", kwargs={"pk": device.id})

    response = auth_client.post(url, {}, format="json")

    assert response.status_code == 400
    assert "patient_id" in response.json()


@pytest.mark.django_db
def test_assign_device_invalid_patient_id_format_returns_bad_request(auth_client, device):
    url = reverse("devices-assign", kwargs={"pk": device.id})

    response = auth_client.post(
        url,
        {"patient_id": "not-a-uuid"},
        format="json",
    )

    assert response.status_code == 400
    assert "patient_id" in response.json()


@pytest.mark.django_db
def test_assign_nonexistent_device_returns_not_found(auth_client, patient):
    url = reverse("devices-assign", kwargs={"pk": uuid.uuid4()})

    response = auth_client.post(
        url,
        {"patient_id": str(patient.id)},
        format="json",
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Device does not exist."}


@pytest.mark.django_db(transaction=True)
def test_concurrent_assignment_only_one_request_succeeds(
    user, patient, second_patient, device
):
    results = []

    def assign(patient_id):
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("devices-assign", kwargs={"pk": device.id})
        response = client.post(
            url,
            {"patient_id": str(patient_id)},
            format="json",
        )
        results.append(response.status_code)

    t1 = Thread(target=assign, args=(patient.id,))
    t2 = Thread(target=assign, args=(second_patient.id,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    device.refresh_from_db()

    assert sorted(results) == [200, 409]
    assert device.assigned_patient_id in {patient.id, second_patient.id}
    assert device.assigned_at is not None

import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from monitoring.models import Device, Patient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username=f"user_{uuid.uuid4().hex[:8]}",
        password="testpass123",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def patient(db):
    return Patient.objects.create(
        first_name="Test",
        last_name="User",
        date_of_birth="1990-01-01",
        mrn=f"MRN-{uuid.uuid4()}",
        is_high_priority=True,
        spi_enabled=True,
    )


@pytest.fixture
def second_patient(db):
    return Patient.objects.create(
        first_name="Another",
        last_name="User",
        date_of_birth="1985-05-05",
        mrn=f"MRN-{uuid.uuid4()}",
        is_high_priority=False,
        spi_enabled=False,
    )


@pytest.fixture
def device(db):
    return Device.objects.create(
        serial_number=f"DEV-{uuid.uuid4()}",
        model="MODEL-X",
    )

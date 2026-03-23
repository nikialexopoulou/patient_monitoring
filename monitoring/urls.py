from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from monitoring.views.alerts import AlertViewSet
from monitoring.views.devices import DeviceViewSet
from monitoring.views.observations import ObservationViewSet
from monitoring.views.patients import PatientViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patients")
router.register(r"devices", DeviceViewSet, basename="devices")
router.register(r"observations", ObservationViewSet, basename="observations")
router.register(r"alerts", AlertViewSet, basename="alerts")

urlpatterns = [
    path("token/", obtain_auth_token),
]
urlpatterns += router.urls

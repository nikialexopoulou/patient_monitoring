from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets

from monitoring.filters import ObservationFilter
from monitoring.models import Observation
from monitoring.serializers.observations import ObservationSerializer
from monitoring.services import generate_alerts_for_observation


class ObservationViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Observation.objects.all().order_by("-recorded_at")
    serializer_class = ObservationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ObservationFilter

    @extend_schema(
        filters=False,
        parameters=[
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description="Filter observations from this datetime",
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description="Filter observations up to this datetime",
            ),
        ],
        responses={200: ObservationSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=ObservationSerializer,
        responses={201: ObservationSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        observation = serializer.save()
        generate_alerts_for_observation(observation)

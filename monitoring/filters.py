import django_filters
from django import forms

from .models import Observation


class ObservationFilterForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        from_dt = cleaned_data.get("from_")
        to_dt = cleaned_data.get("to")

        if from_dt and to_dt and from_dt > to_dt:
            raise forms.ValidationError("'from' must be earlier than or equal to 'to'.")

        return cleaned_data


class ObservationFilter(django_filters.FilterSet):
    from_ = django_filters.IsoDateTimeFilter(
        field_name="recorded_at",
        lookup_expr="gte",
    )
    to = django_filters.IsoDateTimeFilter(
        field_name="recorded_at",
        lookup_expr="lte",
    )

    class Meta:
        model = Observation
        fields = []
        form = ObservationFilterForm

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()
            if "from" in data and "from_" not in data:
                data["from_"] = data.get("from")
        super().__init__(data=data, *args, **kwargs)

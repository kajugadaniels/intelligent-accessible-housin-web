import django_filters
from django import forms
from backend.models import *

class PropertyFilter(django_filters.FilterSet):
    # From / To date range on created_at
    start_date = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="gte",
        label="From",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    end_date = django_filters.DateFilter(
        field_name="created_at__date",
        lookup_expr="lte",
        label="To",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = Property
        # You can extend these later (city, type, category, etc.)
        fields = ["start_date", "end_date"]

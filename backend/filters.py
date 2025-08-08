import django_filters
from django import forms
from users.models import *
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

class RentApplicationFilter(django_filters.FilterSet):
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
    status = django_filters.ChoiceFilter(
        field_name="status",
        label="Application Status",
        choices=[("Pending","Pending"),("Accepted","Accepted"),("Rejected","Rejected"),("Moved Out","Moved Out")],
        empty_label="All",
        widget=forms.Select(attrs={"class":"form-select"})
    )

    class Meta:
        model = RentApplication
        fields = ["start_date", "end_date", "status"]

class ContractFilter(django_filters.FilterSet):
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
    status = django_filters.ChoiceFilter(
        field_name="status",
        label="Contract Status",
        choices=(
            ("Active", "Active"),
            ("Terminated", "Terminated"),
            ("Expired", "Expired"),
            ("Pending", "Pending"),
        ),
        empty_label="All",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    payment_status = django_filters.ChoiceFilter(
        field_name="payment_status",
        label="Payment Status",
        choices=(("Paid", "Paid"), ("Pending", "Pending"), ("Overdue", "Overdue")),
        empty_label="All",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Contract
        fields = ["start_date", "end_date", "status", "payment_status"]
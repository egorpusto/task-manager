import django_filters
from django import forms

from .models import Tag, Task


class TaskFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Search",
    )
    tag = django_filters.ModelChoiceFilter(
        queryset=Tag.objects.all(),
        label="Tag",
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("deadline", "deadline"),
            ("priority", "priority"),
        ),
        field_labels={
            "created_at": "Date created",
            "-created_at": "Date created (newest)",
            "deadline": "Deadline (earliest)",
            "-deadline": "Deadline (latest)",
            "priority": "Priority (low → high)",
            "-priority": "Priority (high → low)",
        },
        widget=forms.Select,
    )

    class Meta:
        model = Task
        fields = ["status", "priority", "tag", "search", "ordering"]

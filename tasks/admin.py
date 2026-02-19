from django.contrib import admin
from django.utils.html import format_html

from .models import Tag, Task


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "task_count")
    search_fields = ("name",)

    def task_count(self, obj):
        return obj.tasks.count()

    task_count.short_description = "Tasks"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "colored_priority",
        "colored_status",
        "deadline",
        "created_at",
    )
    list_filter = ("priority", "status", "tags", "created_at")
    search_fields = ("title", "description", "user__username")
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    fieldsets = (
        ("General", {"fields": ("user", "title", "description")}),
        ("Details", {"fields": ("priority", "status", "deadline", "tags")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def colored_priority(self, obj):
        colors = {"low": "#17a2b8", "medium": "#ffc107", "high": "#dc3545"}
        color = colors.get(obj.priority, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display(),
        )

    colored_priority.short_description = "Priority"

    def colored_status(self, obj):
        colors = {"todo": "#007bff", "in_progress": "#ffc107", "done": "#28a745"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    colored_status.short_description = "Status"

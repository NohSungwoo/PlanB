from django.urls import path

from .views import (
    CalendarDetailView,
    CalendarListView,
    ScheduleCopyView,
    ScheduleDetailView,
    ScheduleListView,
    ScheduleSearchView,
)

urlpatterns = [
    path(
        "<str:calendar_name>",
        CalendarDetailView.as_view(),
        name="calendar",
    ),
    path("calendar", CalendarListView.as_view(), name="calendars"),
    path("schedule", ScheduleListView.as_view(), name="schedules"),
    path(
        "schedule/<int:schedule_id>", ScheduleDetailView.as_view(), name="schedule"
    ),
    path(
        "schedule/<int:schedule_id>/copy", ScheduleCopyView.as_view(), name="schedule-copy"
    ),
    path("schedule/search", ScheduleSearchView.as_view(), name="schedule-search"),
]

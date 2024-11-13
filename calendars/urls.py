from django.urls import path

from .views import (
    CalendarDetailView,
    CalendarListView,
    ScheduleCopyView,
    ScheduleDetailView,
    ScheduleListView,
    ScheduleSearchView,
)

calendar_urls = [
    path(
        "<str:calendar_name>",
        CalendarDetailView.as_view(),
        name="calendar-detail",
    ),
    path("", CalendarListView.as_view(), name="calendar-list"),
]

schedule_urls = [
    path("schedule", ScheduleListView.as_view(), name="schedule-list"),
    path(
        "schedule/<int:schedule_id>",
        ScheduleDetailView.as_view(),
        name="schedule-detail",
    ),
    path(
        "schedule/<int:schedule_id>/copy",
        ScheduleCopyView.as_view(),
        name="schedule-copy",
    ),
    path("schedule/search", ScheduleSearchView.as_view(), name="schedule-search"),
]

urlpatterns = calendar_urls + schedule_urls

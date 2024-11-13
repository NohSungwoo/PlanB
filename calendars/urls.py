from django.urls import path

from .views import (
    CalendarDetailView,
    CalendarListView,
    ScheduleCopyView,
    ScheduleCreateView,
    ScheduleDeleteView,
    ScheduleDetailView,
    ScheduleListView,
    ScheduleSearchView,
    ScheduleUpdateView,
)

urlpatterns = [
    ### Calendar 

    path(
        "<str:calendar_name>",
        CalendarDetailView.as_view(),
        name="calendar-detail",
    ),
    path("", CalendarListView.as_view(), name="calendar-list"),

    ### Schedule

    path("schedule", ScheduleCreateView.as_view(), name="schedule-create"),
    path("schedule", ScheduleListView.as_view(), name="schedule-list"),
    path(
        "schedule/<int:schedule_id>",
        ScheduleDetailView.as_view(),
        name="schedule-detail",
    ),
    path(
        "schedule/<int:schedule_id>",
        ScheduleDeleteView.as_view(),
        name="schedule-delete",
    ),
    path(
        "schedule/<int:schedule_id>",
        ScheduleUpdateView.as_view(),
        name="schedule-update",
    ),
    path(
        "schedule/<int:schedule_id>/copy",
        ScheduleCopyView.as_view(),
        name="schedule-copy",
    ),
    path("schedule/search", ScheduleSearchView.as_view(), name="schedule-search"),
]

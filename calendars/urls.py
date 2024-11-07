from django.urls import path

from calendars.views import (
    CalendarCreateView,
    CalendarDetailView,
    CalendarListView,
    CalendarView,
)

urlpatterns = [
    path("calendar/<str:calendar_name>/", CalendarView.as_view(), name="calendar"),
    path(
        "calendar/<str:calendar_name>",
        CalendarDetailView.as_view(),
        name="calendar-detail",
    ),
    path("calendar", CalendarCreateView.as_view(), name="calendar-create"),
    path("calendar", CalendarListView.as_view(), name="calendar-list"),
]

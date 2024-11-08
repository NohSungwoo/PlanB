from django.urls import path

from calendars.views import CalendarCreateView, CalendarDetailView, CalendarListView

urlpatterns = [
    path(
        "calendar/<str:calendar_name>",
        CalendarDetailView.as_view(),
        name="calendar-detail",
    ),
    path("calendar", CalendarCreateView.as_view(), name="calendar-create"),
    path("calendar", CalendarListView.as_view(), name="calendar-list"),
]

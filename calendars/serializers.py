from rest_framework import serializers as s
from calendars.models import Calendar, Schedule


class CalendarDetailSerializer(s.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ("title",)


class CalendarUpdateSerializer(s.ModelSerializer):
    pass


class CalendarCreateSerializer(s.ModelSerializer):
    pass


class CalendarListSerializer(s.ListSerializer):
    pass


class ScheduleSerializer(s.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "calendar",
            "memo",
            "title",
            "startdate",
            "start_time",
            "end_date",
            "end_time",
            "is_repeat",
        )

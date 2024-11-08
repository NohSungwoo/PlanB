from rest_framework import serializers as s

from calendars.models import Calendar, Schedule


class CalendarDetailSerializer(s.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ("title",)


class CalendarListSerializer(s.Serializer):
    pass


class CalendarCreateSerializer(s.Serializer):
    pass


class ScheduleSerializer(s.Serializer):
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

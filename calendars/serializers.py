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


class ScheduleDetailSerializer(s.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "calendar",
            "memo",
            "title",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "is_repeat",
        )


class ScheduleCreateSerializer(s.Serializer):
    pass


class ScheduleUpdateSerializer(s.Serializer):
    pass


class ScheduleDeleteSerializer(s.Serializer):
    pass


class ScheduleSearchSerializer(s.Serializer):
    pass


class ScheduleListSerializer(s.Serializer):
    pass


class ScheduleCopySerializer(s.Serializer):
    pass


class ScheduleListQuerySerializer(s.Serializer):
    pass


class ScheduleSearchQuerySerializer(s.Serializer):
    pass

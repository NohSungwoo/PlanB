from rest_framework import serializers as s

from calendars.models import Calendar, Schedule


class CalendarDetailSerializer(s.ModelSerializer):
    user = s.StringRelatedField()

    class Meta:
        model = Calendar
        fields = "__all__"


class ScheduleDetailSerializer(s.ModelSerializer):
    participant = s.SlugRelatedField(slug_field="email", read_only=True, many=True)
    memo = s.HyperlinkedRelatedField(
        view_name="memo-detail", read_only=True, allow_null=True
    )

    class Meta:
        model = Schedule
        fields = "__all__"


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


class ScheduleListQuerySerializer(s.Serializer):
    pass


class ScheduleSearchQuerySerializer(s.Serializer):
    pass

from django.contrib.auth import get_user_model
from rest_framework import serializers as s

from calendars.models import Calendar, Schedule

User = get_user_model()


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
    calendar = s.HyperlinkedRelatedField(view_name="title", read_only=True, many=False)

    class Meta:
        model = Schedule
        fields = "__all__"


class ScheduleUpdateSerializer(s.ModelSerializer):
    """
    유저를 초대할때 이메일을 사용할 수 있습니다. 종속 캘린더를 변경할 수 있습니다.
    """

    participant = s.SlugRelatedField(
        slug_field="email", many=True, queryset=User.objects.all()
    )
    calendar = s.SlugRelatedField(slug_field="title", queryset=Calendar.objects.all())

    class Meta:
        model = Schedule
        fields = (
            "title",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "is_repeat",
            "calendar",
            "participant",
        )

from django.contrib.auth import get_user_model
from rest_framework import serializers as s

from calendars.models import Calendar, Schedule
from memos.models import Memo
from memos.serializers import MemoDetailSerializer

User = get_user_model()


class CalendarDetailSerializer(s.ModelSerializer):
    user = s.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Calendar
        fields = "__all__"

    def validate(self, data):
        """
        유저와 title이 고유한지 여부를 테스트합니다.
        """
        request = self.context.get("request")
        if not request:
            raise Exception({"context": "validate시에 context=user가 필요합니다."})

        user = request.user
        title = data.get("title")
        if self.Meta.model.objects.filter(user=user, title=title).exists():
            raise s.ValidationError(
                {"title": f"해당 유저에 타이틀 '{title}'이 이미 존재합니다."}
            )

        return data

    def update(self, instance: Calendar, validated_data) -> Calendar:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ScheduleDetailSerializer(s.ModelSerializer):
    participant = s.PrimaryKeyRelatedField(read_only=True, many=True)
    memo = MemoDetailSerializer(required=False)
    calendar = s.PrimaryKeyRelatedField(read_only=True, many=False)

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

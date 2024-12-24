from random import choice
from types import FunctionType
from typing import Self
from django.contrib.auth import get_user_model
from rest_framework import serializers as s
from rest_framework.fields import ChoiceField

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
                {"title": f"해당 유저에 타이틀 '{title}'이/가 이미 존재합니다."}
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
    calendar = CalendarDetailSerializer(required=False)

    class Meta:
        model = Schedule
        fields = "__all__"


class ScheduleUpdateSerializer(s.ModelSerializer):
    """
    유저를 초대할때 이메일을 사용할 수 있습니다. 종속 캘린더를 변경할 수 있습니다.
    """

    participant = s.SlugRelatedField(
        queryset=User.objects.all(),
        required=False,
        slug_field="email",
        many=True,
    )
    calendar = s.SlugRelatedField(
        queryset=Calendar.objects.all(),
        required=False,
        slug_field="title",
    )

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


class ScheduleViewChoices(s.Serializer):
    """
    ScheduleListView GET 요청의 query_params 중에서 `view` Choices를 명시하기 위해 사용되는 serializer 입니다.
    """

    view = ChoiceField(
        choices=(
            "monthly",
            "daily",
            "weekly",
        )
    )


class ScheduleDirectionChoices(s.Serializer):
    """
    ScheduleListView GET 요청의 query_params 중에서 `direction` Choices를 명시하기 위해 사용하는 serializer 입니다.
    """

    direction = ChoiceField(choices=("next", "previous"))

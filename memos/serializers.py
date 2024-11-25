from django.contrib.auth import get_user_model
from rest_framework import serializers as s

from calendars.models import Schedule
from memos.models import Memo, MemoSet
from todos.models import Todo

User = get_user_model()


class MemoDetailSerializer(s.ModelSerializer):
    memo_set = s.PrimaryKeyRelatedField(queryset=MemoSet.objects.all())
    memo_schedule = s.PrimaryKeyRelatedField(
        queryset=Schedule.objects.all(), required=False
    )
    memo_todo = s.PrimaryKeyRelatedField(queryset=Todo.objects.all(), required=False)

    class Meta:
        model = Memo
        fields = (
            "title",
            "memo_set",
            "text",
            "memo_schedule",
            "memo_todo",
        )

    def validate_memo_schedule(self, schedule_id: int) -> int:
        """
        Field Level Validation, null일 경우 실행되지 않습니다.
        """
        if not Schedule.objects.exists(id=schedule_id):
            raise s.ValidationError("Schedule이 존재하지 않습니다.")

        return schedule_id

    def validate_memo_todo(self, todo_id: int) -> int:
        """
        Field Level Validation, null일 경우 실행되지 않습니다.
        """
        if not Todo.objects.exists(id=todo_id):
            raise s.ValidationError("Todo가 존재하지 않습니다.")

        return todo_id


class MemoSetDetailSerializer(s.ModelSerializer):
    user = s.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MemoSet
        fields = "__all__"

    def validate(self, data):
        """
        유저와 타이틀이 고유한지 여부를 테스트합니다.
        """
        request = self.context.get("request")
        user = request.user
        title = data.get("title")

        if MemoSet.objects.filter(user=user, title=title).exists():
            raise s.ValidationError(
                {"title": f"해당 유저에 타이틀 '{title}'이 이미 존재합니다."}
            )

        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

from django.contrib.auth import get_user_model
from rest_framework import serializers as s

from calendars.models import Schedule
from memos.models import Memo, MemoSet
from todos.models import Todo

User = get_user_model()


class MemoDetailSerializer(s.ModelSerializer):
    memo_set = s.PrimaryKeyRelatedField(queryset=MemoSet.objects.all(), required=False)
    memo_schedule = s.PrimaryKeyRelatedField(read_only=True)
    memo_todo = s.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Memo
        fields = (
            "id",
            "title",
            "memo_set",
            "text",
            "memo_schedule",
            "memo_todo",
        )

    def create(self, validated_data) -> Memo:
        request = self.context.get("request")

        user = request.user
        title = validated_data.pop("title")
        text = validated_data.pop("text")

        # get default memo_set if no "memo_set" found
        memo_set = validated_data.pop(
            "memo_set",
            # TODO - abstract default memo_set name
            MemoSet.objects.get(
                user=user,
                title="Memo",
            ),
        )

        instance = Memo.objects.create(title=title, text=text, memo_set=memo_set)

        return instance

    def update(self, instance: Memo, validated_data) -> Memo:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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

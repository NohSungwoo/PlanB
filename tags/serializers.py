from rest_framework import serializers as s

from calendars.models import Schedule
from memos.models import Memo
from tags.models import Tag
from todos.models import Todo


class TagDetailSerializer(s.ModelSerializer):
    user = s.StringRelatedField()
    schedule = s.PrimaryKeyRelatedField(many=True, read_only=True)
    memo = s.PrimaryKeyRelatedField(many=True, read_only=True)
    todo = s.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = "__all__"


class TagLabelSerializer(s.ModelSerializer):
    todo = s.PrimaryKeyRelatedField(queryset=Todo.objects.all(), many=True)
    memo = s.PrimaryKeyRelatedField(queryset=Memo.objects.all(), many=True)
    schedule = s.PrimaryKeyRelatedField(queryset=Schedule.objects.all(), many=True)

    class Meta:
        model = Tag
        fields = (
            "todo",
            "memo",
            "schedule",
        )


class TagTitleSerializer(s.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("title",)

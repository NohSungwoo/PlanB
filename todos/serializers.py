from rest_framework import serializers as s

from memos.serializers import MemoDetailSerializer
from todos.models import SubTodo, Todo, TodoSet


class TodoSetDetailSerializer(s.ModelSerializer):
    user = s.StringRelatedField()

    class Meta:
        model = TodoSet
        fields = "__all__"


class SubTodoDetailSerializer(s.ModelSerializer):
    todo = s.PrimaryKeyRelatedField(read_only=True)
    memo = MemoDetailSerializer(required=False)
    complete_date = s.DateTimeField(allow_null=True, read_only=True)

    class Meta:
        model = SubTodo
        fields = (
            "id",
            "todo",
            "memo",
            "title",
            "start_date",
            "complete_date",
        )


class TodoDetailSerializer(s.ModelSerializer):
    todo_set = s.PrimaryKeyRelatedField(read_only=True)
    memo = MemoDetailSerializer()
    todo_sub = SubTodoDetailSerializer(many=True, read_only=True)
    complete_date = s.DateTimeField(allow_null=True, read_only=True)

    class Meta:
        model = Todo
        fields = (
            "id",
            "todo_set",
            "memo",
            "title",
            "start_date",
            "complete_date",
            "todo_sub",  # reverse relationship see todos/models.py
        )

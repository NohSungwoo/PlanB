from rest_framework import serializers as s

from todos.models import SubTodo, Todo, TodoSet


class TodoSetDetailSerializer(s.ModelSerializer):
    user = s.StringRelatedField()

    class Meta:
        model = TodoSet
        fields = "__all__"


class SubTodoDetailSerializer(s.ModelSerializer):
    todo = s.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SubTodo
        fields = "__all__"


class TodoDetailSerializer(s.ModelSerializer):
    todo_set = s.StringRelatedField()
    memo = s.StringRelatedField()
    todo_sub = SubTodoDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Todo
        fields = (
            "todo_set",
            "memo",
            "title",
            "start_date",
            "complete_date",
            "todo_sub",  # reverse relationship
        )

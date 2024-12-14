from rest_framework import serializers as s
from rest_framework.exceptions import NotFound, ParseError

from memos.models import Memo
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

    def create(self, validated_data):
        try:
            todo = Todo.objects.get(pk=validated_data.pop("todo_id"))
        except Todo.DoesNotExist:
            raise NotFound

        sub_todo_memo = validated_data.pop("memo", None)
        sub_todo_title = validated_data.pop("title")
        sub_todo_start_date = validated_data.pop("start_date")

        if sub_todo_memo:
            memo_title = sub_todo_memo.pop("title")
            memo_text = sub_todo_memo.pop("text")
            memo_set = sub_todo_memo.pop("memo_set")

            memo = Memo.objects.create(
                title=memo_title, text=memo_text, memo_set=memo_set
            )

            sub_todo = SubTodo.objects.create(
                todo=todo,
                memo=memo,
                title=sub_todo_title,
                start_date=sub_todo_start_date,
            )
        else:
            sub_todo = SubTodo.objects.create(
                todo=todo, title=sub_todo_title, start_date=sub_todo_start_date
            )

        return sub_todo


class TodoDetailSerializer(s.ModelSerializer):
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
            "todo_sub",
        )

    def create(self, validated_data):
        todo_set = ("todo_set", TodoSet.objects.get(user=validated_data.pop("user"), title="Todo"))
        memo = validated_data.pop("memo", None)
        todo_title = validated_data.pop("title", None)

        memo_title = memo.pop("title", None)
        memo_text = memo.pop("text", None)

        memo = Memo.objects.create(title=memo_title, text=memo_text)

        try:
            todo_start = validated_data["start_date"]

        except KeyError:
            raise ParseError("Need start_date")

        todo = Todo.objects.create(
            todo_set=todo_set, memo=memo, title=todo_title, start_date=todo_start
        )

        return todo

    def update(self, instance, validated_data):
        todo = instance
        todo_set = ("todo_set", TodoSet.objects.get(user=validated_data.pop("user"), title="Todo"))
        memo = validated_data.pop("memo", None)
        todo_title = validated_data.pop("title")
        todo_start_date = validated_data.pop("start_date")

        todo.todo_set = todo_set
        todo.title = todo_title
        todo.start_date = todo_start_date

        if memo:
            todo.memo.title = memo.pop("title")
            todo.memo.text = memo.pop("text")
            todo.memo.memo_set = memo.pop("memo_set")
            todo.memo.save()

        todo.save()

        return todo

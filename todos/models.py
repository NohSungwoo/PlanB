from django.db import models

from common.models import CommonModel


class TodoSet(CommonModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="user_todo_set"
    )
    title = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "title"], name="unique_todo")
        ]


class Todo(CommonModel):
    todo_set = models.ForeignKey(
        "todos.TodoSet", on_delete=models.CASCADE, default=1, related_name="set_todo"
    )
    memo = models.OneToOneField(
        "memos.Memo", on_delete=models.CASCADE, related_name="memo_todo", null=True
    )
    title = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    complete_date = models.DateTimeField(null=True, blank=True)


class SubTodo(CommonModel):
    todo = models.ForeignKey(
        "todos.todo", on_delete=models.CASCADE, related_name="todo_sub"
    )
    memo = models.OneToOneField(
        "memos.Memo", on_delete=models.CASCADE, related_name="memo_sub"
    )
    title = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    complete_date = models.DateTimeField(null=True, blank=True)

from django.db import models

from common.models import CommonModel


class TodoSet(CommonModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="user_todo_set"
    )
    title = models.CharField(max_length=50)


class Todo(CommonModel):
    todo_set = models.ForeignKey(
        "todos.TodoSet", on_delete=models.CASCADE, related_name="set_todo"
    )
    memo = models.OneToOneField(
        "memos.Memo", on_delete=models.CASCADE, related_name="memo_todo"
    )
    title = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    complete_date = models.DateTimeField(null=True, blank=True)

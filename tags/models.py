from django.db import models

from common.models import CommonModel


class Tag(CommonModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="user_tags"
    )
    calendar = models.ManyToManyField(
        "calendars.Calendar", related_name="calendar_tags"
    )
    todo = models.ManyToManyField("todos.Todo", related_name="todo_tags")
    memo = models.ManyToManyField("memos.Memo", related_name="memo_tags")
    title = models.CharField(max_length=30)

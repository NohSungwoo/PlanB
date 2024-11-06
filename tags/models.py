from django.db import models

from common.models import CommonModel


class Tag(CommonModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="user_tags"
    )
    schedule = models.ManyToManyField(
        "calendars.Schedule", related_name="schedule_tags"
    )
    todo = models.ManyToManyField("todos.Todo", related_name="todo_tags")
    memo = models.ManyToManyField("memos.Memo", related_name="memo_tags")
    title = models.CharField(max_length=30, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "title"], name="unique_tag")
        ]

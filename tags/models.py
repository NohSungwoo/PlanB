from django.db import models
from common.models import CommonModel


class Tag(CommonModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="tags")
    calendar = models.ManyToManyField("calendars.Calendar", related_name="tags")
    todo = models.ManyToManyField("todos.Todo", related_name="tags")
    memo = models.ManyToManyField("memos.Memo", related_name="tags")
    title = models.CharField(max_length=30)

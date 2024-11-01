from django.db import models
from common.models import CommonModel


class MemoSet(CommonModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_memo_set")
    title = models.CharField(max_length=50)


class Memo(CommonModel):
    calendar = models.OneToOneField("calendars.Calendar", on_delete=models.CASCADE, related_name="calendar_memo")
    todo = models.OneToOneField("todos.Todo", on_delete=models.CASCADE, related_name="todo_memo")
    title = models.CharField(max_length=50 ,default="새로운 메모")
    text = models.TextField(null=True, blank=True)
    is_cal = models.BooleanField(default=False)
    is_todo = models.BooleanField(default=False)

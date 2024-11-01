from django.db import models

from common.models import CommonModel


class TodoSet(CommonModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="user_todo_set"
    )
    title = models.CharField(max_length=50)


class Todo(CommonModel):
    memo = models.OneToOneField(
        "memos.Memo", on_delete=models.CASCADE, related_name="memo_todo"
    )
    tags = models.ManyToManyField("tags.Tag", related_name="tags_todo")
    title = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    complete_date = models.DateTimeField(null=True, blank=True)

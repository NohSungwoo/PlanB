from django.db import models

from common.models import CommonModel


class MemoSet(CommonModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="user_memo_set"
    )
    title = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "title"], name="unique_user_title")
        ]


class Memo(CommonModel):
    memo_set = models.ForeignKey(
        "memos.MemoSet", on_delete=models.CASCADE, related_name="set_memo"
    )
    title = models.CharField(max_length=50, default="새로운 메모")
    text = models.TextField(null=True, blank=True)



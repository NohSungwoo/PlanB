from django.db import models
from common.models import CommonModel


class Calendar(CommonModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_calendar")
    title = models.CharField(max_length=50)


class Schedule(CommonModel):
    calendar = models.ForeignKey("calendars.Calendar", on_delete=models.CASCADE, related_name="calendar_schedule")
    participant = models.ManyToManyField("users.User", related_name="user_schedule")
    memo = models.OneToOneField("memos.Memo", on_delete=models.CASCADE, related_name="memo_schedule")
    title = models.CharField(max_length=50)
    google_url = models.URLField(max_length=255, null=True)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    is_repeat = models.BooleanField()

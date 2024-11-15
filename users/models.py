from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import CommonModel


class User(AbstractUser, CommonModel):
    class GenderChoices(models.TextChoices):
        MALE = ("male", "Male")
        FEMALE = ("female", "Female")

    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30)
    gender = models.CharField(max_length=20, choices=GenderChoices)
    birthday = models.DateField()
    photo = models.URLField(null=True)
    google_cal_url = models.URLField(max_length=255, null=True)
    is_active = models.BooleanField(default=False)
    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

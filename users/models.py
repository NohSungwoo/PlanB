from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models import CommonModel


class User(AbstractUser, CommonModel):
    class GenderChoices(models.TextChoices):
        MALE = ("male", "Male")
        FEMALE = ("female", "Female")

    email = models.EmailField(unique=True)
    username = None
    first_name = None
    last_name = None
    nickname = models.CharField(max_length=30)
    gender = models.CharField(max_length=20 ,choices=GenderChoices)
    birthday = models.PositiveIntegerField()
    photo = models.URLField(null=True)
    google_cal_url = models.URLField(max_length=255, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

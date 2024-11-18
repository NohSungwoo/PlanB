from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import CommonModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Need Email")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


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
    REQUIRED_FIELDS = ["birthday"]

    objects = CustomUserManager()

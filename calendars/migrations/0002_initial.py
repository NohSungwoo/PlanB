# Generated by Django 5.1.2 on 2024-11-06 00:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("calendars", "0001_initial"),
        ("memos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="calendar",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_calendar",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="schedule",
            name="calendar",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="calendar_schedule",
                to="calendars.calendar",
            ),
        ),
        migrations.AddField(
            model_name="schedule",
            name="memo",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="memo_schedule",
                to="memos.memo",
            ),
        ),
        migrations.AddField(
            model_name="schedule",
            name="participant",
            field=models.ManyToManyField(
                related_name="user_schedule", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddConstraint(
            model_name="calendar",
            constraint=models.UniqueConstraint(
                fields=("user", "title"), name="unique_calendar"
            ),
        ),
    ]

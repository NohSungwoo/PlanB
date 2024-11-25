# Generated by Django 5.1.3 on 2024-11-23 02:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calendars", "0003_alter_schedule_end_date_alter_schedule_end_time_and_more"),
        ("memos", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schedule",
            name="memo",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="memo_schedule",
                to="memos.memo",
            ),
        ),
    ]

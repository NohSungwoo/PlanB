# Generated by Django 5.1.2 on 2024-11-01 01:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("memos", "0001_initial"),
        ("todos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="memo",
            name="todo",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todo_memo",
                to="todos.todo",
            ),
        ),
        migrations.AddField(
            model_name="memoset",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_memo_set",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

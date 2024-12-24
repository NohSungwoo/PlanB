# Generated by Django 5.1.3 on 2024-12-08 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("memos", "0003_alter_memo_memo_set"),
        ("todos", "0003_alter_todo_memo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subtodo",
            name="memo",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="memo_sub",
                to="memos.memo",
            ),
        ),
        migrations.AlterField(
            model_name="todo",
            name="todo_set",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="set_todo",
                to="todos.todoset",
            ),
        ),
    ]
# Generated by Django 5.1.2 on 2024-11-01 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('calendars', '0002_initial'),
        ('memos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=30)),
                ('calendar', models.ManyToManyField(related_name='calendar_tags', to='calendars.calendar')),
                ('memo', models.ManyToManyField(related_name='memo_tags', to='memos.memo')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

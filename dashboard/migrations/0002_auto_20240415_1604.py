# Generated by Django 3.2 on 2024-04-15 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dashboard',
            name='description',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='title',
        ),
    ]

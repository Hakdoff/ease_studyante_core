# Generated by Django 3.2 on 2024-03-17 02:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('academic_record', '0010_auto_20240317_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

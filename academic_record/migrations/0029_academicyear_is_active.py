# Generated by Django 3.2 on 2024-05-09 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic_record', '0028_alter_assessment_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicyear',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]

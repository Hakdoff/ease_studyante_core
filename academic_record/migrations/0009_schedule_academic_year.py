# Generated by Django 3.2 on 2024-03-16 03:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academic_record', '0008_auto_20240316_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='academic_year',
            field=models.ForeignKey(default='739a9ff7-3714-49f7-bbda-ae233916f499', on_delete=django.db.models.deletion.CASCADE, to='academic_record.academicyear'),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.1.7 on 2025-03-23 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsAccounts', '0004_job_end_job_time_job_start_job_time_job_wait_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='average_wait_time',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

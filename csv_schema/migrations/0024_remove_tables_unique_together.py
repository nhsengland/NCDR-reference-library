# Generated by Django 2.1.5 on 2019-02-12 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('csv_schema', '0023_remove_userprofile'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='table',
            unique_together=set(),
        ),
    ]
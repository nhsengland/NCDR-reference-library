# Generated by Django 2.1.5 on 2019-02-13 10:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csv_schema', '0025_add_schema_to_database'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='column',
            name='slug',
        ),
    ]
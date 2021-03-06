# Generated by Django 2.1.7 on 2019-03-08 08:45

from django.db import migrations


def create_version(apps, schema_editor):
    Version = apps.get_model("ncdr", "Version")
    Version.objects.create(is_published=True)


def delete_version(apps, schema_editor):
    Version = apps.get_model("ncdr", "Version")
    Version.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [("ncdr", "0001_initial")]
    operations = [migrations.RunPython(create_version, reverse_code=delete_version)]

# Generated by Django 2.1.7 on 2019-09-17 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ncdr", "0010_auto_20190822_1341")]

    operations = [
        migrations.AlterField(
            model_name="version", name="files_hash", field=models.TextField(null=True)
        )
    ]

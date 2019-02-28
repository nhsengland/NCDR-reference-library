# Generated by Django 2.1.7 on 2019-02-28 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("ncdr", "0009_add_created_by_and_created_at_to_version")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="current_version",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ncdr.Version",
            ),
        )
    ]

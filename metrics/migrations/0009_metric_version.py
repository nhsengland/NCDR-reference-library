# Generated by Django 2.1.11 on 2020-01-30 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ncdr", "0014_auto_20200130_1535"),
        ("metrics", "0008_auto_20191029_1722"),
    ]

    operations = [
        migrations.AddField(
            model_name="metric",
            name="version",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="metrics",
                to="ncdr.Version",
            ),
        )
    ]
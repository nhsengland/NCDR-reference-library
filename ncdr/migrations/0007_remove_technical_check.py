# Generated by Django 2.1.7 on 2019-03-11 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("ncdr", "0006_switch_charfields_for_textfields")]

    operations = [migrations.RemoveField(model_name="column", name="technical_check")]

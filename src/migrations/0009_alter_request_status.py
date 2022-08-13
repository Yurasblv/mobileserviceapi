# Generated by Django 4.1 on 2022-08-11 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0008_alter_customuser_phone_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="request",
            name="status",
            field=models.CharField(
                choices=[("PROCESS", "PROCESS"), ("DONE", "DONE")],
                default="PROCESS",
                max_length=30,
            ),
        ),
    ]

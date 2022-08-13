# Generated by Django 4.1 on 2022-08-08 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0003_alter_customuser_last_login"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customuser",
            options={
                "verbose_name": "custom_user",
                "verbose_name_plural": "custom_users",
            },
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="email",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="last_name",
        ),
    ]
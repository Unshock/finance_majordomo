# Generated by Django 4.2 on 2023-11-22 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="fields_to_display",
        ),
        migrations.AlterUniqueTogether(
            name="portfolio",
            unique_together={("name", "user")},
        ),
    ]

# Generated by Django 4.2 on 2023-11-12 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0005_alter_asset_issuedate"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="primary_boardid",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="Основной режим торгов"
            ),
        ),
    ]

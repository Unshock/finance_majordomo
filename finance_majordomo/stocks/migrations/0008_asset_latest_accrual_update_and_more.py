# Generated by Django 4.2 on 2023-11-12 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0007_alter_asset_creation_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="latest_accrual_update",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Дата последнего обновления информации о начислениях",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="creation_date",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Дата создания"),
        ),
    ]

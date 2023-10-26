# Generated by Django 4.2 on 2023-10-26 18:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("stocks", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="stocksofuser",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="bondofuser",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="assetsofuser",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.asset"
            ),
        ),
        migrations.AddField(
            model_name="assetsofuser",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="assetofportfolio",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.asset"
            ),
        ),
        migrations.AddField(
            model_name="assetofportfolio",
            name="portfolio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="users.portfolio"
            ),
        ),
        migrations.AddField(
            model_name="asset",
            name="portfolios",
            field=models.ManyToManyField(
                related_name="asset",
                through="stocks.AssetOfPortfolio",
                to="users.portfolio",
            ),
        ),
        migrations.AddField(
            model_name="asset",
            name="users",
            field=models.ManyToManyField(
                related_name="asset1",
                through="stocks.AssetsOfUser",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="stocksofuser",
            name="stock",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.stock"
            ),
        ),
        migrations.AddField(
            model_name="shareshistoricaldata",
            name="share",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.stock"
            ),
        ),
        migrations.AddField(
            model_name="bondshistoricaldata",
            name="bond",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.bond"
            ),
        ),
        migrations.AddField(
            model_name="bondofuser",
            name="bond",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.bond"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="shareshistoricaldata",
            unique_together={("share", "tradedate")},
        ),
        migrations.AlterUniqueTogether(
            name="bondshistoricaldata",
            unique_together={("bond", "tradedate")},
        ),
    ]

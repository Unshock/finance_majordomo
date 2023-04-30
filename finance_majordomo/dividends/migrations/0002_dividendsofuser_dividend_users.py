# Generated by Django 4.2 on 2023-04-27 19:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dividends", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DividendsOfUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.BooleanField(
                        default=False,
                        help_text="Shows if the dividend is got by user",
                        verbose_name="dividend status",
                    ),
                ),
                (
                    "dividend",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dividends.dividend",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Дивиденд пользователя",
                "verbose_name_plural": "Дивиденды пользователей",
                "ordering": ["dividend"],
            },
        ),
        migrations.AddField(
            model_name="dividend",
            name="users",
            field=models.ManyToManyField(
                blank=True,
                related_name="dividend",
                through="dividends.DividendsOfUser",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
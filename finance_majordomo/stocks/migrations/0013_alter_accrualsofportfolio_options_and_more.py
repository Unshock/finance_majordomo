# Generated by Django 4.2 on 2023-12-24 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_remove_user_fields_to_display_and_more"),
        ("stocks", "0012_rename_dividendsofportfolio_accrualsofportfolio_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="accrualsofportfolio",
            options={
                "ordering": ["accrual"],
                "verbose_name": "Начисление портфеля",
                "verbose_name_plural": "Начисления портфеля",
            },
        ),
        migrations.AlterField(
            model_name="accrualsofportfolio",
            name="is_received",
            field=models.BooleanField(
                default=False,
                help_text="shows if portfolio got accrual",
                verbose_name="Accrual status",
            ),
        ),
        migrations.CreateModel(
            name="Accrual",
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
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creation date"
                    ),
                ),
                ("date", models.DateField(verbose_name="Accrual date")),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=8,
                        verbose_name="Accrual amount for one asset",
                    ),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="stocks.asset"
                    ),
                ),
                (
                    "portfolios",
                    models.ManyToManyField(
                        blank=True,
                        related_name="accrual",
                        through="stocks.AccrualsOfPortfolio",
                        to="users.portfolio",
                    ),
                ),
            ],
            options={
                "verbose_name": "Начисление",
                "verbose_name_plural": "Начисления",
                "ordering": ["creation_date", "asset", "amount"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="accrualsofportfolio",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="accrualsofportfolio",
            name="accrual",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="stocks.accrual",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="accrualsofportfolio",
            unique_together={("portfolio", "accrual")},
        ),
        migrations.RemoveField(
            model_name="accrualsofportfolio",
            name="dividend",
        ),
        migrations.DeleteModel(
            name="Dividend",
        ),
    ]

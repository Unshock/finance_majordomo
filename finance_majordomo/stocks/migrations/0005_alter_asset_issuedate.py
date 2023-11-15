# Generated by Django 4.2 on 2023-11-12 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0004_bond_face_value"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="issuedate",
            field=models.DateField(
                blank=True, null=True, verbose_name="Дата начала торгов"
            ),
        ),
    ]
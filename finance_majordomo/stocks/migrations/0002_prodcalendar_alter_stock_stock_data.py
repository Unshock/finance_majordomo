# Generated by Django 4.1.4 on 2023-02-23 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProdCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=10, verbose_name='Дата')),
                ('date_status', models.CharField(choices=[('0', 'Working'), ('1', 'Nonworking')], max_length=10, verbose_name='Статус дня')),
            ],
        ),
        migrations.AlterField(
            model_name='stock',
            name='stock_data',
            field=models.JSONField(verbose_name='Данные об акции'),
        ),
    ]

# Generated by Django 2.0.3 on 2018-04-24 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20180424_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='type',
            field=models.CharField(choices=[('0', 'Сумма'), ('1', 'Процент')], max_length=1, verbose_name='Тип'),
        ),
    ]

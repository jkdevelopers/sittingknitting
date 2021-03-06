# Generated by Django 2.0.3 on 2018-04-05 22:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=18, validators=[django.core.validators.RegexValidator(code='invalid_length_phone', message='Введите номер телефона в формате +7 (XXX) XXX-XX-XX', regex='\\+7 \\([0-9]{3}\\) [0-9]{3}-[0-9]{2}-[0-9]{2}')], verbose_name='Телефон'),
        ),
    ]

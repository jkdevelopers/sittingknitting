# Generated by Django 2.0.3 on 2018-04-17 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20180417_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(blank=True, to='core.OrderItem', verbose_name='Элементы'),
        ),
    ]
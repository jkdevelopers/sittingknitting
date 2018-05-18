# Generated by Django 2.0.3 on 2018-05-18 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_product_modifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Показывать на сайте'),
        ),
        migrations.AlterField(
            model_name='product',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Разрешить покупку'),
        ),
    ]
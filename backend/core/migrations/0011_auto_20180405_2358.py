# Generated by Django 2.0.3 on 2018-04-05 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_category_product'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
    ]
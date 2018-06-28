# Generated by Django 2.0.3 on 2018-06-11 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20180610_1430'),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=200, verbose_name='Значение')),
            ],
            options={
                'verbose_name': 'Параметр',
                'verbose_name_plural': 'Параметры',
            },
        ),
        migrations.CreateModel(
            name='PropertyHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('default', models.CharField(blank=True, max_length=200, verbose_name='Значение по умолчанию')),
                ('filters', models.BooleanField(default=True, verbose_name='Использовать для фильтров')),
                ('modifications', models.BooleanField(default=False, verbose_name='Использовать для модификаций')),
            ],
            options={
                'verbose_name': 'Параметр',
                'verbose_name_plural': 'Параметры',
            },
        ),
        migrations.RemoveField(
            model_name='modification',
            name='main_product',
        ),
        migrations.RemoveField(
            model_name='modification',
            name='product',
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name': 'Элемент', 'verbose_name_plural': 'Элементы'},
        ),
        migrations.RemoveField(
            model_name='category',
            name='filter',
        ),
        migrations.RemoveField(
            model_name='order',
            name='items',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.Order', verbose_name='Заказ'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='main',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='core.Product', verbose_name='Корневой товар модификаций'),
        ),
        migrations.DeleteModel(
            name='Modification',
        ),
        migrations.AddField(
            model_name='propertyhandler',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='core.Category', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='property',
            name='handler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='core.PropertyHandler'),
        ),
        migrations.AddField(
            model_name='property',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='core.Product', verbose_name='Товар'),
        ),
    ]
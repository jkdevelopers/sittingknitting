# Generated by Django 2.0.3 on 2018-06-11 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20180610_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('default', models.CharField(max_length=200, verbose_name='Значение по умолчанию')),
            ],
            options={
                'verbose_name': 'Параметр',
                'verbose_name_plural': 'Параметры',
            },
        ),
        migrations.RemoveField(
            model_name='property',
            name='category',
        ),
        migrations.RemoveField(
            model_name='category',
            name='filter',
        ),
        migrations.DeleteModel(
            name='Property',
        ),
        migrations.AddField(
            model_name='propertyhandler',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='core.Category', verbose_name='Категория'),
        ),
    ]
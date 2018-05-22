# Generated by Django 2.0.3 on 2018-05-22 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20180518_2115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modification',
            name='type',
        ),
        migrations.AddField(
            model_name='category',
            name='filter',
            field=models.CharField(blank=True, default='', help_text='Цвет, размер, модель и т.п.', max_length=50, verbose_name='Параметр модификаций'),
        ),
    ]

# Generated by Django 2.0.3 on 2018-05-18 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20180509_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='Modification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=200, verbose_name='Тип')),
                ('value', models.CharField(max_length=200, verbose_name='Значение')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Модификация',
                'verbose_name_plural': 'Модификации',
            },
        ),
    ]

# Generated by Django 2.0.3 on 2018-04-05 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='uid',
            field=models.CharField(max_length=100, unique=True, verbose_name='UID'),
        ),
    ]
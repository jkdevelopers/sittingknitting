# Generated by Django 2.0.3 on 2018-04-01 13:42

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=100, verbose_name='UID')),
                ('template', models.CharField(max_length=100, verbose_name='Template')),
                ('modification', models.CharField(max_length=100, verbose_name='Modification')),
                ('name', models.CharField(blank=True, default='', max_length=100, verbose_name='Name')),
                ('attributes', jsonfield.fields.JSONField(blank=True, default=dict, verbose_name='Attributes')),
            ],
            options={
                'verbose_name': 'Component',
                'verbose_name_plural': 'Components',
            },
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-19 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='value',
            field=models.TextField(default=''),
        ),
    ]

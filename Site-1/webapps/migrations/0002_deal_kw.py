# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-04 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='kw',
            field=models.CharField(default='', max_length=200),
        ),
    ]

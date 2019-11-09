# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-11-01 07:37
from __future__ import unicode_literals

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='sign',
            field=models.CharField(default=user.models.default_sign, max_length=50, verbose_name='个人签名'),
        ),
    ]

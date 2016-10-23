# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-10-23 07:58
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0012_quest_parent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mission',
            options={'ordering': ['quest__title', 'order_number', 'name'], 'verbose_name': 'задание', 'verbose_name_plural': 'задания'},
        ),
        migrations.AlterField(
            model_name='mission',
            name='order_number',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)], verbose_name='номер задания'),
        ),
    ]

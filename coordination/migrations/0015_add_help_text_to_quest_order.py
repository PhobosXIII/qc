# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-05 08:47
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0014_quest_order_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='order_number',
            field=models.PositiveSmallIntegerField(default=1, help_text='Влияет на порядок отображения линий.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)], verbose_name='номер линии'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-07 07:04
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0009_add_fields_for_nonlinear_quest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hint',
            name='delay',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(360)], verbose_name='время отправления'),
        ),
    ]

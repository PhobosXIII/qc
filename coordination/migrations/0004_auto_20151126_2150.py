# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0003_auto_20151123_1821'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mission',
            options={'ordering': ['order_number', 'name'], 'verbose_name': 'задание', 'verbose_name_plural': 'задания'},
        ),
        migrations.AlterField(
            model_name='hint',
            name='text',
            field=ckeditor.fields.RichTextField(verbose_name='текст подсказки'),
        ),
        migrations.AlterField(
            model_name='mission',
            name='text',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='текст задания'),
        ),
        migrations.AlterField(
            model_name='quest',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='описание'),
        ),
    ]

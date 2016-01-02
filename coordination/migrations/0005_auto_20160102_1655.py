# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0004_auto_20151126_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='text',
            field=ckeditor.fields.RichTextField(verbose_name='текст сообщения'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(verbose_name='заголовок', max_length=255)),
                ('text', models.TextField(verbose_name='текст новости')),
                ('is_published', models.BooleanField(verbose_name='опубликована', default=False)),
                ('published_date', models.DateTimeField(null=True, verbose_name='дата публикации', blank=True)),
            ],
            options={
                'verbose_name': 'новость',
                'verbose_name_plural': 'новости',
                'ordering': ['-published_date'],
            },
        ),
    ]

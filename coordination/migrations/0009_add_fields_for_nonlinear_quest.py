# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0008_remove_quest_old_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='keylog',
            name='points',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='баллы'),
        ),
        migrations.AddField(
            model_name='mission',
            name='points',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='баллы'),
        ),
        migrations.AddField(
            model_name='quest',
            name='game_over',
            field=models.DateTimeField(blank=True, null=True, verbose_name='конец игры'),
        ),
    ]

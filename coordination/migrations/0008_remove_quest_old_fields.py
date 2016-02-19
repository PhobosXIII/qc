# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0007_move_data_to_membership'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quest',
            name='organizer',
        ),
        migrations.RemoveField(
            model_name='quest',
            name='players',
        ),
        migrations.AlterField(
            model_name='quest',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL, verbose_name='создатель'),
        ),
    ]

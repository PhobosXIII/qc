# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coordination', '0005_auto_20160102_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('O', 'Организатор'), ('P', 'Игрок'), ('A', 'Агент')], default='P', max_length=1, verbose_name='роль')),
            ],
            options={
                'verbose_name': 'Участник квеста',
                'verbose_name_plural': 'Участники квеста',
            },
        ),
        migrations.AlterModelOptions(
            name='currentmission',
            options={'ordering': ['-mission__order_number', 'start_time'], 'verbose_name': 'текущее задание', 'verbose_name_plural': 'текущие задания'},
        ),
        migrations.AddField(
            model_name='quest',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL, verbose_name='создатель'),
        ),
        migrations.AddField(
            model_name='membership',
            name='quest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordination.Quest', verbose_name='квест'),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        migrations.AddField(
            model_name='quest',
            name='members',
            field=models.ManyToManyField(related_name='members', through='coordination.Membership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('quest', 'user')]),
        ),
    ]

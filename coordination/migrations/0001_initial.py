# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
from django.conf import settings
import django.utils.timezone
import coordination.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentMission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('start_time', models.DateTimeField(verbose_name='время начала задания', default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'текущее задание',
                'verbose_name_plural': 'текущие задания',
                'ordering': ['-mission', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('text', models.TextField(verbose_name='текст подсказки')),
                ('delay', models.PositiveSmallIntegerField(verbose_name='время отправления', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(90)])),
                ('order_number', models.PositiveSmallIntegerField(verbose_name='номер подсказки', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)])),
            ],
            options={
                'verbose_name': 'подсказка',
                'verbose_name_plural': 'подсказки',
                'ordering': ['order_number'],
            },
        ),
        migrations.CreateModel(
            name='Keylog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('key', models.CharField(verbose_name='ключ', max_length=30)),
                ('fix_time', models.DateTimeField(verbose_name='время ключа')),
                ('is_right', models.BooleanField(verbose_name='правильный ключ', default=False)),
            ],
            options={
                'verbose_name': 'история ключей',
                'verbose_name_plural': 'история ключей',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('text', models.TextField(verbose_name='текст сообщения')),
                ('is_show', models.BooleanField(verbose_name='отображать', default=True)),
            ],
            options={
                'verbose_name': 'сообщение',
                'verbose_name_plural': 'сообщения',
            },
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(verbose_name='название', max_length=100, blank=True)),
                ('name_in_table', models.CharField(verbose_name='название в табличке', max_length=100, blank=True)),
                ('text', models.TextField(verbose_name='текст задания', blank=True)),
                ('picture', models.ImageField(verbose_name='картинка', upload_to=coordination.models.mission_file_name, blank=True)),
                ('key', models.CharField(verbose_name='ключ', max_length=30, blank=True)),
                ('order_number', models.PositiveSmallIntegerField(verbose_name='номер задания', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99)])),
                ('is_finish', models.BooleanField(verbose_name='финиш', default=False)),
            ],
            options={
                'verbose_name': 'задание',
                'verbose_name_plural': 'задания',
                'ordering': ['order_number'],
            },
        ),
        migrations.CreateModel(
            name='Quest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(verbose_name='название', max_length=255)),
                ('start', models.DateTimeField(null=True, verbose_name='старт', blank=True)),
                ('description', models.TextField(verbose_name='описание', blank=True)),
                ('status', models.CharField(choices=[('NTS', 'Не запущен'), ('STR', 'Запущен'), ('END', 'Завершен')], verbose_name='статус', default='NTS', max_length=3)),
                ('is_published', models.BooleanField(verbose_name='опубликован', default=False)),
                ('organizer', models.ForeignKey(related_name='organizer', verbose_name='организатор', to=settings.AUTH_USER_MODEL)),
                ('players', models.ManyToManyField(verbose_name='игроки', to=settings.AUTH_USER_MODEL, related_name='players', blank=True)),
            ],
            options={
                'verbose_name': 'квест',
                'verbose_name_plural': 'квесты',
                'ordering': ['start'],
            },
        ),
        migrations.AddField(
            model_name='mission',
            name='quest',
            field=models.ForeignKey(verbose_name='квест', to='coordination.Quest'),
        ),
        migrations.AddField(
            model_name='message',
            name='quest',
            field=models.ForeignKey(verbose_name='квест', to='coordination.Quest'),
        ),
        migrations.AddField(
            model_name='keylog',
            name='mission',
            field=models.ForeignKey(verbose_name='задание', to='coordination.Mission'),
        ),
        migrations.AddField(
            model_name='keylog',
            name='player',
            field=models.ForeignKey(verbose_name='игрок', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hint',
            name='mission',
            field=models.ForeignKey(verbose_name='задание', to='coordination.Mission'),
        ),
        migrations.AddField(
            model_name='currentmission',
            name='mission',
            field=models.ForeignKey(verbose_name='задание', to='coordination.Mission'),
        ),
        migrations.AddField(
            model_name='currentmission',
            name='player',
            field=models.ForeignKey(verbose_name='игрок', to=settings.AUTH_USER_MODEL),
        ),
    ]

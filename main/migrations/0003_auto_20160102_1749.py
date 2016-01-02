# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20151126_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('question', models.CharField(verbose_name='вопрос', max_length=255)),
                ('answer', ckeditor.fields.RichTextField(verbose_name='ответ')),
            ],
            options={
                'verbose_name': 'вопрос-ответ',
                'ordering': ['question'],
                'verbose_name_plural': 'вопросы-ответы',
            },
        ),
        migrations.CreateModel(
            name='HelpCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(verbose_name='заголовок', max_length=255)),
                ('order_number', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)], verbose_name='номер')),
            ],
            options={
                'verbose_name': 'категория помощи',
                'ordering': ['order_number'],
                'verbose_name_plural': 'категории помощи',
            },
        ),
        migrations.AddField(
            model_name='faq',
            name='category',
            field=models.ForeignKey(verbose_name='категория', to='main.HelpCategory'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_organizers_features_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    group = Group.objects.create(name='organizers_features')

    ContentType = apps.get_model("contenttypes", "ContentType")
    Quest = apps.get_model("coordination", "Quest")
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(Quest)
    permission_add = Permission.objects.get_or_create(codename='add_quest', content_type=content_type)[0]
    group.permissions.add(permission_add)


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0002_add_organizers_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='quest',
            name='type',
            field=models.CharField(default='L', choices=[('L', 'Линейный'), ('NL', 'Нелинейный'), ('LNL', 'Линейно-нелинейный')], verbose_name='тип', max_length=3),
        ),
        migrations.AlterField(
            model_name='mission',
            name='name',
            field=models.CharField(blank=True, verbose_name='название', max_length=100, help_text='В основном для сюжетных игр, например, Панофобия, Колдунья и т.д. Отображается игрокам в координации.'),
        ),
        migrations.AlterField(
            model_name='mission',
            name='name_in_table',
            field=models.CharField(blank=True, verbose_name='название в табличке', max_length=100, help_text='Как правило ответ на задание. Отображается в итоговой табличке.'),
        ),
        migrations.RunPython(create_organizers_features_group),
    ]

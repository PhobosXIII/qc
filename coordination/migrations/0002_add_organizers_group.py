# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_organizers_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    group = Group.objects.create(name='organizers')

    ContentType = apps.get_model("contenttypes", "ContentType")
    Quest = apps.get_model("coordination", "Quest")
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(Quest)
    permission_add = Permission.objects.get_or_create(codename='add_quest', content_type=content_type)[0]
    group.permissions.add(permission_add)


class Migration(migrations.Migration):
    dependencies = [
        ('coordination', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_organizers_group),
    ]

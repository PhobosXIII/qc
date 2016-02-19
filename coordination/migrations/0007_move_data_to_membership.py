# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def assign_creator(apps, schema_editor):
    Quest = apps.get_model("coordination", "Quest")
    for quest in Quest.objects.all():
        quest.creator = quest.organizer
        quest.save()


def move_organizer_and_players(apps, schema_editor):
    Quest = apps.get_model("coordination", "Quest")
    Membership = apps.get_model("coordination", "Membership")
    for quest in Quest.objects.all():
        Membership.objects.create(quest=quest, user=quest.organizer, role="O")
        for player in quest.players.all():
            Membership.objects.create(quest=quest, user=player, role="P")


class Migration(migrations.Migration):

    dependencies = [
        ('coordination', '0006_create_membership_model'),
    ]

    operations = [
        migrations.RunPython(assign_creator),
        migrations.RunPython(move_organizer_and_players),
    ]

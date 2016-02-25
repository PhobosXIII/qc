from django.contrib import admin

from coordination.models import Quest, Mission, Hint, CurrentMission, Keylog, Message, Membership
from qc import settings
from qc.admin import admin_site


class MemberInline(admin.TabularInline):
    model = Membership
    extra = 3
    ordering = ('role', 'user__first_name')


class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'role')
    list_filter = ('quest', 'role')
    ordering = ['quest', 'role']


class QuestAdmin(admin.ModelAdmin):
    fields = [('title', 'is_published', 'status'), 'type', 'creator', 'start', 'game_over', 'description']
    list_display = ('title', 'creator', 'start', 'type')
    inlines = [MemberInline]
    ordering = ['-start']


class HintInline(admin.TabularInline):
    model = Hint
    extra = 3
    fields = ('order_number', 'text', 'delay')


class MissionAdmin(admin.ModelAdmin):
    fields = ['quest', ('name', 'order_number', 'is_finish'), 'name_in_table', 'text', ('key', 'points'), ]
    if settings.QC_UPLOAD:
        fields += ('picture',)
    inlines = [HintInline]
    list_display = ('__str__', 'quest', 'points', )
    list_filter = ('quest', )
    ordering = ('quest', 'order_number')


class CurrentMissionAdmin(admin.ModelAdmin):
    list_display = ('player', 'get_quest', 'mission', 'start_time')
    ordering = ['-mission', 'start_time']
    list_filter = ('mission__quest', )


class KeylogAdmin(admin.ModelAdmin):
    list_display = ('player', 'get_quest', 'mission', 'key', 'fix_time', 'is_right', 'points')
    ordering = ['fix_time']
    list_filter = ('is_right', 'player', 'mission', 'mission__quest')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('strip_text', 'is_show')
    list_filter = ('quest', )


def get_quest(self, obj):
    return obj.mission.quest
get_quest.short_description = 'квест'


CurrentMissionAdmin.get_quest = get_quest
KeylogAdmin.get_quest = get_quest


admin_site.register(Quest, QuestAdmin)
admin_site.register(Membership, MemberAdmin)
admin_site.register(Mission, MissionAdmin)
admin_site.register(CurrentMission, CurrentMissionAdmin)
admin_site.register(Keylog, KeylogAdmin)
admin_site.register(Message, MessageAdmin)

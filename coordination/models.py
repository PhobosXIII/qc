from datetime import timedelta
from itertools import groupby

from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags

from coordination.utils import get_timedelta_with_now, time_in_minutes, generate_random_username, \
    generate_random_password, get_timedelta


def mission_file_name(instance, filename):
    ext = filename.split('.')[-1].lower()
    filename = "{0}-{1}.{2}".format(instance.order_number, timezone.now().strftime("%d-%m-%Y-%H-%M-%S"), ext)
    return '/'.join(['mission_imgs', str(instance.quest.creator.pk), str(instance.quest.pk), filename])


class Quest(models.Model):
    LINEAR = 'L'
    NONLINEAR = 'NL'
    LINE_NONLINEAR = 'LNL'
    MULTILINEAR = 'ML'
    NOT_STARTED = 'NTS'
    STARTED = 'STR'
    ENDED = 'END'

    TYPES = (
        (LINEAR, 'Линейный'),
        (NONLINEAR, 'Нелинейный'),
        (LINE_NONLINEAR, 'Линейно-нелинейный'),
        (MULTILINEAR, 'Многолинейный'),
    )
    STATUSES = (
        (NOT_STARTED, 'Не запущен'),
        (STARTED, 'Запущен'),
        (ENDED, 'Завершен'),
    )
    title = models.CharField('название', max_length=255)
    start = models.DateTimeField('старт', null=True, blank=True)
    description = RichTextField('описание', blank=True)
    type = models.CharField('тип', max_length=3, choices=TYPES, default=LINEAR)
    status = models.CharField('статус', max_length=3, choices=STATUSES, default=NOT_STARTED)
    is_published = models.BooleanField('опубликован', default=False)
    organizer_name = models.CharField('Имя организатора', max_length=30,
                                      help_text='Имя организатора для данной игры. Полезно для творческого '
                                                'объединения организаторов.')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='создатель', related_name='creator',
                                on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='members')
    game_over = models.DateTimeField('конец игры', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, editable=False, null=True, blank=True)
    order_number = models.PositiveSmallIntegerField('номер линии', default=1,
                                                    help_text='Влияет на порядок отображения линий.',
                                                    validators=[MinValueValidator(1), MaxValueValidator(99)])

    class Meta:
        verbose_name = 'квест'
        verbose_name_plural = 'квесты'
        ordering = ['start']

    @property
    def published(self):
        quest = self
        if self.parent:
            quest = self.parent
        return quest.is_published

    @property
    def not_started(self):
        quest = self
        if self.parent:
            quest = self.parent
        return quest.status == Quest.NOT_STARTED

    @property
    def started(self):
        quest = self
        if self.parent:
            quest = self.parent
        return quest.status == Quest.STARTED

    @property
    def ended(self):
        quest = self
        if self.parent:
            quest = self.parent
        return quest.status == Quest.ENDED

    @property
    def linear(self):
        return self.type == self.LINEAR

    @property
    def nonlinear(self):
        return self.type == self.NONLINEAR

    @property
    def line_nonlinear(self):
        return self.type == self.LINE_NONLINEAR

    @property
    def multilinear(self):
        return self.type == self.MULTILINEAR

    @property
    def is_game_over(self):
        quest = self
        if self.parent:
            quest = self.parent
        if quest.game_over:
            return timezone.now() >= quest.game_over
        else:
            return False

    @property
    def rest_quest(self):
        quest = self
        if self.parent:
            quest = self.parent
        if quest.started and not quest.is_game_over:
            return get_timedelta(quest.game_over)
        else:
            return None

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(Quest, self).save(*args, **kwargs)
        if is_create:
            if not self.parent:
                Membership.objects.create(quest=self, user=self.creator, role=Membership.ORGANIZER)
                name = 'agent{0}'.format(self.pk)
                username = generate_random_username(name)
                password = generate_random_password()
                agent = User.objects.create_user(username=username, password=password, first_name=name,
                                                 last_name=password)
                Membership.objects.create(quest=self, user=agent, role=Membership.AGENT)
                Mission.objects.create(quest=self, name_in_table='Старт', order_number=0)
            Mission.objects.create(quest=self, name_in_table='Финиш', order_number=1, is_finish=True)

    def begin(self):
        if self.not_started:
            self.status = self.STARTED
        elif self.started:
            self.status = self.NOT_STARTED
        self.save()

    def end(self):
        if self.started:
            self.status = self.ENDED
        elif self.ended:
            self.status = self.STARTED
        self.save()

    def publish(self):
        self.is_published = not self.is_published
        self.save()

    def lines(self):
        return Quest.objects.filter(parent=self).order_by('order_number')

    def missions(self):
        if self.multilinear:
            return Mission.objects.filter(quest__in=self.lines()).order_by('quest__order_number', 'order_number')
        else:
            return Mission.objects.filter(quest=self).order_by('order_number')

    def current_missions(self):
        return CurrentMission.objects.filter(mission__quest=self)

    def current_missions_multilinear(self, player):
        return CurrentMission.objects.filter(mission__quest__in=self.lines(), player=player)

    def next_mission_number(self):
        if self.parent:
            return len(self.missions())
        else:
            return len(self.missions()) - 1

    def start_mission(self):
        return Mission.objects.get(quest=self, order_number=0)

    def finish_mission(self):
        return Mission.objects.filter(quest=self, is_finish=True).first()

    def messages(self):
        return Message.objects.filter(quest=self)

    def organizers(self):
        return self.members.filter(membership__role=Membership.ORGANIZER)

    def players(self):
        return self.members.filter(membership__role=Membership.PLAYER).order_by('first_name')

    def agents(self):
        return self.members.filter(membership__role=Membership.AGENT)

    def players_ext(self):
        all_missions = self.missions().filter(order_number__gt=0, is_finish=False)
        players = self.members.filter(membership__role=Membership.PLAYER)
        for player in players:
            player.last_time = Keylog.last_time(self, player)
            player.points = Keylog.total_points(self, player)
            missions = Mission.completed_missions(self, player)
            other_missions = [i for i in all_missions if i not in missions]
            player.num_missions = len(missions)
            if self.multilinear:
                player.missions = self.multiline_missions_str(missions)
                player.other_missions = self.multiline_missions_str(other_missions)
            else:
                player.missions = ', '.join(str(i.table_name) for i in missions)
                player.other_missions = ', '.join(str(i.table_name) for i in other_missions)
        return players

    def missions_ext(self):
        all_players = self.members.filter(membership__role=Membership.PLAYER)
        missions = self.missions().filter(order_number__gt=0, is_finish=False)
        for mission in missions:
            keylogs = mission.right_keylogs()
            players = [i.player for i in keylogs]
            mission.players = ', '.join(str(i) for i in players)
            other_players = [i for i in all_players if i not in players]
            mission.other_players = ', '.join(str(i) for i in other_players)
            mission.num_players = len(keylogs)
        return missions

    @staticmethod
    def coming_quests():
        now = timezone.now() - timedelta(hours=6)
        return Quest.objects.filter(is_published=True, parent__isnull=True, start__gte=now)

    @staticmethod
    def my_quests(user):
        return Quest.objects.filter(membership__user=user, parent__isnull=True)

    @staticmethod
    def multiline_missions_str(missions):
        line_format = "{0}: {1}"
        missions = sorted(missions, key=lambda x: x.quest.order_number)
        iter = groupby(missions, key=lambda x: x.quest)
        quest_missions = []
        for quest, missions in iter:
            line_str = ', '.join(str(i.table_name) for i in missions)
            quest_missions.append(line_format.format(quest.title, line_str))
        missions_str = ' ___ '.join(i for i in quest_missions)
        return missions_str


class OrganizerManager(models.Manager):
    def get_queryset(self):
        return super(OrganizerManager, self).get_queryset().filter(role=Membership.ORGANIZER)


class PlayerManager(models.Manager):
    def get_queryset(self):
        return super(PlayerManager, self).get_queryset().filter(role=Membership.PLAYER)


class AgentManager(models.Manager):
    def get_queryset(self):
        return super(AgentManager, self).get_queryset().filter(role=Membership.AGENT)


class Membership(models.Model):
    ORGANIZER = 'O'
    PLAYER = 'P'
    AGENT = 'A'

    ROLES = (
        (ORGANIZER, 'Организатор'),
        (PLAYER, 'Игрок'),
        (AGENT, 'Агент'),
    )
    quest = models.ForeignKey(Quest, verbose_name='квест', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='пользователь', on_delete=models.CASCADE)
    role = models.CharField('роль', max_length=1, choices=ROLES, default=PLAYER)
    objects = models.Manager()
    organizers = OrganizerManager()
    players = PlayerManager()
    agents = AgentManager()

    class Meta:
        verbose_name = 'Участник квеста'
        verbose_name_plural = 'Участники квеста'
        unique_together = ('quest', 'user')

    @property
    def organizer(self):
        return self.role == self.ORGANIZER

    @property
    def player(self):
        return self.role == self.PLAYER

    @property
    def agent(self):
        return self.role == self.AGENT


class Mission(models.Model):
    quest = models.ForeignKey(Quest, verbose_name='квест', on_delete=models.CASCADE)
    name = models.CharField('название', max_length=100, blank=True,
                            help_text='В основном для сюжетных игр, например, Панофобия, Колдунья и т.д. '
                                      'Отображается игрокам в координации.')
    name_in_table = models.CharField('название в табличке', max_length=100, blank=True,
                                     help_text='Как правило ответ на задание. Отображается в итоговой табличке.')
    text = RichTextField('текст задания', blank=True)
    picture = models.ImageField('картинка', upload_to=mission_file_name, blank=True)
    key = models.CharField('ключ', max_length=30, blank=True)
    order_number = models.PositiveSmallIntegerField('номер задания',
                                                    validators=[MinValueValidator(0), MaxValueValidator(99)])
    is_finish = models.BooleanField(u'финиш', default=False)
    points = models.PositiveSmallIntegerField('баллы', default=0)

    class Meta:
        verbose_name = 'задание'
        verbose_name_plural = 'задания'
        ordering = ['quest__title', 'order_number', 'name']

    @property
    def is_start(self):
        return self.order_number == 0

    def __str__(self):
        if self.is_start:
            return 'Старт'
        elif self.is_finish:
            if self.quest.line_nonlinear:
                return 'Финиш{0}'.format(". " + self.name if self.name else "")
            else:
                return 'Финиш'
        else:
            return 'Задание {0}{1}{2}'.format(self.order_number,
                                              ". " + self.name if self.name else "",
                                              " (" + self.name_in_table + ")" if self.name_in_table else "")

    @property
    def short_name(self):
        if self.is_start or self.is_finish:
            return self.__str__()
        else:
            return 'Задание {0}{1}'.format(self.order_number, ". " + self.name if self.name else "")

    @property
    def medium_name(self):
        if self.is_start or self.is_finish:
            return self.__str__()
        else:
            return '{0}{1}{2}'.format(self.order_number, ". " + self.name if self.name else "",
                                      " (" + self.name_in_table + ")" if self.name_in_table else "")

    @property
    def table_name(self):
        if self.is_start or self.is_finish:
            return self.__str__()
        else:
            return '{0}{1}'.format(self.order_number, ". " + self.name_in_table if self.name_in_table else "")

    @property
    def total_hints_time(self):
        hint = Hint.objects.filter(mission=self).order_by('order_number').last()
        if hint is not None:
            return hint.abs_delay
        else:
            return 0

    def save(self, *args, **kwargs):
        super(Mission, self).save(*args, **kwargs)
        if not self.is_start and not self.is_finish:
            Mission.update_finish_number(self.quest)

    def hints(self):
        return Hint.objects.filter(mission=self)

    @staticmethod
    def hints_in_nl(quest, missions):
        display_hints = []
        rest_hints = []
        if quest.nonlinear:
            minutes = time_in_minutes(get_timedelta_with_now(quest.start))
            for mission in missions:
                hints = mission.hints()
                for hint in hints:
                    if hint.abs_delay <= minutes:
                        display_hints.append(hint)
                    else:
                        rest_hints.append(hint)
        return display_hints, rest_hints

    def next_hint_number(self):
        return len(self.hints()) + 1

    def is_completed(self, player):
        keylog = Keylog.objects.filter(mission=self, player=player, is_right=True).first()
        return keylog is not None

    def is_current(self, player):
        quest = self.quest
        if quest.nonlinear:
            member = quest.membership_set.filter(user=player).first()
            result = member and member.player
        else:
            current_mission = CurrentMission.objects.filter(mission=self, player=player).first()
            result = current_mission is not None
        return result

    def right_keylogs(self):
        keylogs = Keylog.objects.filter(mission=self, is_right=True)
        return keylogs.order_by('player', 'mission__order_number').distinct('player', 'mission__order_number')

    def as_json(self):
        return {
            "name": self.short_name,
            "text": self.text
        }

    @staticmethod
    def update_finish_number(quest):
        missions = quest.missions()
        order_number = missions.filter(is_finish=False).last().order_number + 1
        missions.filter(is_finish=True).update(order_number=order_number)

    @staticmethod
    def completed_missions(quest, player):
        keylogs = Keylog.get_keylogs(quest, player, True)
        keylogs = keylogs.order_by('fix_time', 'mission__id').distinct('fix_time', 'mission__id')
        return [i.mission for i in keylogs]


class Hint(models.Model):
    mission = models.ForeignKey(Mission, verbose_name='задание', on_delete=models.CASCADE)
    text = RichTextField('текст подсказки')
    delay = models.PositiveSmallIntegerField('время отправления',
                                             validators=[MinValueValidator(1), MaxValueValidator(360)])
    order_number = models.PositiveSmallIntegerField('номер подсказки',
                                                    validators=[MinValueValidator(1), MaxValueValidator(99)])

    class Meta:
        verbose_name = 'подсказка'
        verbose_name_plural = 'подсказки'
        ordering = ['order_number']

    def __str__(self):
        return 'Подсказка {0}'.format(self.order_number)

    @property
    def abs_delay(self):
        hints = Hint.objects.filter(mission=self.mission, order_number__lte=self.order_number)
        aggregation = hints.aggregate(abs_delay=models.Sum('delay'))
        return aggregation.get('abs_delay', self.delay)

    @property
    def time_in_nl(self):
        time = None
        quest = self.mission.quest
        if quest.nonlinear:
            time = quest.start + timedelta(minutes=self.abs_delay)
        return time

    def as_json(self):
        return {
            "title": self.__str__(),
            "delay": self.delay,
            "text": self.text
        }

    @staticmethod
    def as_json_array(hints):
        array = []
        for hint in hints:
            array.append(hint.as_json())
        return array


class CurrentMission(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='игрок', on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, verbose_name='задание', on_delete=models.CASCADE)
    start_time = models.DateTimeField('время начала задания', default=timezone.now)

    class Meta:
        verbose_name = 'текущее задание'
        verbose_name_plural = 'текущие задания'
        ordering = ['-mission__order_number', 'start_time']

    def __str__(self):
        return '{0} - {1}'.format(self.player, self.mission)

    @property
    def alarm(self):
        if self.mission.is_start or self.mission.is_finish:
            return False
        minutes = time_in_minutes(get_timedelta_with_now(self.start_time))
        threshold = self.mission.total_hints_time + 30
        return minutes >= threshold

    def display_hints(self):
        display_hints = []
        minutes = time_in_minutes(get_timedelta_with_now(self.start_time))
        hints = self.mission.hints()
        for hint in hints:
            if hint.abs_delay <= minutes:
                display_hints.append(hint)
        return display_hints

    def next_hint_time(self):
        next_hint_time = None
        minutes = time_in_minutes(get_timedelta_with_now(self.start_time))
        hints = self.mission.hints()
        for hint in hints:
            if hint.abs_delay > minutes:
                next_hint_time = self.start_time + timedelta(minutes=hint.abs_delay)
                break
        return next_hint_time


class Keylog(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='игрок', on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, verbose_name='задание', on_delete=models.CASCADE)
    key = models.CharField('ключ', max_length=30)
    fix_time = models.DateTimeField('время ключа')
    is_right = models.BooleanField('правильный ключ', default=False)
    points = models.PositiveSmallIntegerField('баллы', default=0)

    class Meta:
        verbose_name = 'история ключей'
        verbose_name_plural = 'история ключей'

    def __str__(self):
        return self.key

    @staticmethod
    def right_keylogs(missions):
        keylogs = Keylog.objects.filter(mission__in=missions, is_right=True)
        return keylogs.order_by('player', 'mission__order_number').distinct('player', 'mission__order_number')

    @staticmethod
    def wrong_keylogs(player, mission):
        return Keylog.objects.filter(player=player, mission=mission, is_right=False)

    @staticmethod
    def wrong_keylogs_format(player, mission):
        wrong_keys = Keylog.wrong_keylogs(player, mission)
        return ', '.join(str(i) for i in wrong_keys)

    @staticmethod
    def total_points(quest, player):
        keylogs = Keylog.get_keylogs(quest, player, True)
        keylogs = keylogs.order_by('mission__id').distinct('mission__id')
        total_points = 0
        for keylog in keylogs:
            total_points += keylog.points
        return total_points

    @staticmethod
    def last_time(quest, player):
        keylog = None
        keylogs = Keylog.get_keylogs(quest, player, True)
        if keylogs:
            keylog = keylogs.order_by('-fix_time').first()
        return keylog.fix_time if keylog else timezone.now()

    @staticmethod
    def get_keylogs(quest, player, is_right):
        if quest.multilinear:
            keylogs = Keylog.objects.filter(mission__quest__in=quest.lines(), player=player, is_right=is_right)
        else:
            keylogs = Keylog.objects.filter(mission__quest=quest, player=player, is_right=is_right)
        return keylogs


class Message(models.Model):
    quest = models.ForeignKey(Quest, verbose_name='квест', on_delete=models.CASCADE)
    text = RichTextField('текст сообщения')
    is_show = models.BooleanField('отображать', default=True)

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'

    def strip_text(self):
        return strip_tags(self.text)

    def show(self):
        self.is_show = not self.is_show
        self.save()

    def as_json(self):
        return {
            "text": self.text
        }

    @staticmethod
    def as_json_array(messages):
        array = []
        for message in messages:
            array.append(message.as_json())
        return array

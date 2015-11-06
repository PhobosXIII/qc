from datetime import datetime
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Quest(models.Model):
    STATUSES = (
        ('NTS', 'Не запущен'),
        ('STR', 'Запущен'),
        ('END', 'Завершен'),
    )
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='организатор', related_name='organizer')
    title = models.CharField('название', max_length=255)
    start = models.DateTimeField('старт', null=True, blank=True)
    description = models.TextField('описание', blank=True)
    status = models.CharField('статус', max_length=3, choices=STATUSES, default='NTS')
    is_published = models.BooleanField('опубликован', default=False)
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='игроки', related_name='players',
                                     blank=True)

    class Meta:
        verbose_name = 'квест'
        verbose_name_plural = 'квесты'
        ordering = ['start']

    @property
    def not_started(self):
        return self.status == 'NTS'

    @property
    def started(self):
        return self.status == 'STR'

    @property
    def ended(self):
        return self.status == 'END'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_create = not self.pk
        super(Quest, self).save(*args, **kwargs)
        if is_create:
            start_mission = Mission(quest=self, name_in_table='Старт', order_number=0)
            finish_mission = Mission(quest=self, name_in_table='Финиш', order_number=1, is_finish=True)
            start_mission.save()
            finish_mission.save()

    def begin(self):
        if self.not_started:
            self.status = 'STR'
        elif self.started:
            self.status = 'NTS'
        self.save()

    def end(self):
        if self.started:
            self.status = 'END'
        elif self.ended:
            self.status = 'STR'
        self.save()

    def publish(self):
        self.is_published = not self.is_published
        self.save()

    @staticmethod
    def coming_quests():
        now = timezone.now()
        return Quest.objects.filter(is_published=True, start__gte=now)

    def missions(self):
        return Mission.objects.filter(quest=self)

    def current_missions(self):
        return CurrentMission.objects.filter(mission__quest=self)

    def next_mission_number(self):
        return len(self.missions()) - 1

    def start_mission(self):
        return Mission.objects.get(quest=self, order_number=0)


class Mission(models.Model):
    quest = models.ForeignKey(Quest, verbose_name='квест')
    name = models.CharField('название', max_length=100, blank=True)
    name_in_table = models.CharField('название в табличке', max_length=100, blank=True)
    text = models.TextField('текст задания', blank=True)
    media_file = models.URLField('медиафайл', blank=True)
    key = models.CharField('ключ', max_length=30, blank=True)
    order_number = models.PositiveSmallIntegerField('номер задания',
                                                    validators=[MinValueValidator(0), MaxValueValidator(99)])
    is_finish = models.BooleanField(u'финиш', default=False)

    class Meta:
        verbose_name = 'задание'
        verbose_name_plural = 'задания'
        ordering = ['order_number']

    @property
    def is_start(self):
        return self.order_number == 0

    def __str__(self):
        if self.is_start:
            return 'Старт'
        elif self.is_finish:
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
    def table_name(self):
        if self.is_start or self.is_finish:
            return self.__str__()
        else:
            return '{0}{1}'.format(self.order_number, ". " + self.name_in_table if self.name_in_table else "")

    def save(self, *args, **kwargs):
        super(Mission, self).save(*args, **kwargs)
        if not self.is_start and not self.is_finish:
            Mission.update_finish_number(self.quest)

    def hints(self):
        return Hint.objects.filter(mission=self)

    def next_hint_number(self):
        return len(self.hints()) + 1

    @staticmethod
    def update_finish_number(quest):
        missions = quest.missions()
        finish = missions.filter(is_finish=True).first()
        finish.order_number = missions.filter(is_finish=False).last().order_number + 1
        finish.save()


class Hint(models.Model):
    mission = models.ForeignKey(Mission, verbose_name='задание')
    text = models.CharField('подсказка', max_length=255)
    delay = models.PositiveSmallIntegerField('время отправления',
                                             validators=[MinValueValidator(1), MaxValueValidator(90)])
    order_number = models.PositiveSmallIntegerField('номер подсказки',
                                                    validators=[MinValueValidator(1), MaxValueValidator(99)])

    class Meta:
        verbose_name = 'подсказка'
        verbose_name_plural = 'подсказки'
        ordering = ['order_number']

    def __str__(self):
        return 'Подсказка {0}'.format(self.order_number)


class CurrentMission(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='игрок')
    mission = models.ForeignKey(Mission, verbose_name='задание')
    start_time = models.DateTimeField('время начала задания', default=datetime.now)

    def __str__(self):
        return '{0} - {1}'.format(self.player, self.mission)

    class Meta:
        verbose_name = 'текущее задание'
        verbose_name_plural = 'текущие задания'
        ordering = ['-mission', 'start_time']


class Keylog(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='игрок')
    mission = models.ForeignKey(Mission, verbose_name='задание')
    key = models.CharField('ключ', max_length=30)
    fix_time = models.DateTimeField('время ключа')
    is_right = models.BooleanField('правильный ключ', default=False)

    class Meta:
        verbose_name = 'история ключей'
        verbose_name_plural = 'история ключей'

    def __str__(self):
        return self.key

    @staticmethod
    def right_keylogs(missions):
        return Keylog.objects.filter(mission__in=missions, is_right=True)

    @staticmethod
    def wrong_keylogs(player, mission):
        return Keylog.objects.filter(player=player, mission=mission, is_right=False)

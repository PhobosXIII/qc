from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Quest(models.Model):
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='организатор', related_name='organizer')
    title = models.CharField('название', max_length=255)
    start = models.DateTimeField('старт', null=True, blank=True)
    description = models.TextField('описание', blank=True)
    ended = models.BooleanField('завершен', default=False)
    is_published = models.BooleanField('опубликован', default=False)
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='игроки', related_name='players',
                                     blank=True)

    class Meta:
        verbose_name = 'квест'
        verbose_name_plural = 'квесты'

    def __str__(self):
        return self.title

    def publish(self):
        self.is_published = not self.is_published
        self.save()

    @staticmethod
    def coming_quests():
        now = timezone.now()
        return Quest.objects.filter(is_published=True, start__gte=now)

    def missions(self):
        return Mission.objects.filter(quest=self)

    def next_mission_number(self):
        return len(self.missions())


class Mission(models.Model):
    quest = models.ForeignKey(Quest, verbose_name='квест')
    name = models.CharField('название', max_length=100, blank=True)
    name_in_table = models.CharField('название в табличке', max_length=100, blank=True)
    text = models.TextField('текст задания', blank=True)
    picture = models.URLField('картинка', blank=True)
    key = models.CharField('ключ', max_length=50, blank=True)
    order_number = models.PositiveSmallIntegerField('номер задания', validators=[MinValueValidator(0), MaxValueValidator(99)])

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
        else:
            return 'Задание {0}{1}{2}'.format(self.order_number,
                                              ". " + self.name if self.name else "",
                                              " (" + self.name_in_table + ")" if self.name_in_table else "")

    def hints(self):
        return Hint.objects.filter(mission=self)

    def next_hint_number(self):
        return len(self.hints()) + 1


class Hint(models.Model):
    mission = models.ForeignKey(Mission, verbose_name='задание')
    text = models.CharField('подсказка', max_length=255)
    delay = models.PositiveSmallIntegerField('время отправления', validators=[MinValueValidator(1), MaxValueValidator(90)])
    order_number = models.PositiveSmallIntegerField('номер подсказки', validators=[MinValueValidator(1), MaxValueValidator(99)])

    class Meta:
        verbose_name = 'подсказка'
        verbose_name_plural = 'подсказки'
        ordering = ['order_number']

    def __str__(self):
        return 'Подсказка {0}'.format(self.order_number)

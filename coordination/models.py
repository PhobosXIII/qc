from django.contrib.auth.models import User
from django.db import models


class Quest(models.Model):
    organizer = models.ForeignKey(User, verbose_name='организатор', related_name='organizer')
    title = models.CharField('название', max_length=255)
    start = models.DateTimeField('старт', null=True, blank=True)
    description = models.TextField('описание', blank=True)
    ended = models.BooleanField('завершен', default=False)
    is_published = models.BooleanField('опубликован', default=False)
    players = models.ManyToManyField(User, verbose_name='игроки', related_name='players', blank=True)

    class Meta:
        verbose_name = 'квест'
        verbose_name_plural = 'квесты'

    def __str__(self):
        return self.title

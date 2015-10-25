from django.conf import settings
from django.db import models


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

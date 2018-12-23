from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class News(models.Model):
    title = models.CharField('заголовок', max_length=255)
    text = RichTextField('текст новости')
    is_published = models.BooleanField('опубликована', default=False)
    published_date = models.DateTimeField('дата публикации', blank=True, null=True)

    class Meta:
        verbose_name = 'новость'
        verbose_name_plural = 'новости'
        ordering = ['-published_date']

    def __str__(self):
        return self.title


class HelpCategory(models.Model):
    title = models.CharField('заголовок', max_length=255)
    order_number = models.PositiveSmallIntegerField('номер',
                                                    validators=[MinValueValidator(1), MaxValueValidator(99)])

    class Meta:
        verbose_name = 'категория помощи'
        verbose_name_plural = 'категории помощи'
        ordering = ['order_number']

    def __str__(self):
        return self.title


class Faq(models.Model):
    category = models.ForeignKey(HelpCategory, verbose_name='категория')
    question = models.CharField('вопрос', max_length=255)
    answer = RichTextField('ответ')
    order_number = models.PositiveSmallIntegerField('номер',
                                                    validators=[MinValueValidator(1), MaxValueValidator(99)])

    class Meta:
        verbose_name = 'вопрос-ответ'
        verbose_name_plural = 'вопросы-ответы'
        ordering = ['order_number']

    def __str__(self):
        return self.question

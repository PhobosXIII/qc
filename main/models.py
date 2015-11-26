from ckeditor.fields import RichTextField
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

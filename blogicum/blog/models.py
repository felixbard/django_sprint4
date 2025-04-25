# blog/models.py
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class TimeIsPublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True)

    class Meta():
        abstract = True

    def __str__(self):
        return (f'{self.is_published=}, {self.created_at=}')


class Category(TimeIsPublishedModel):
    """Категория."""

    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        max_length=64, unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:50]


class Location(TimeIsPublishedModel):
    """Местоположение."""

    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return (f'{self.id} '
                f'{self.name[:50]} Добавлен:{self.created_at:%d.%m.%Y} '
                f' {"Опубликован" if self.is_published else "Не опубликован"}')


class Post(TimeIsPublishedModel):
    """Публикация."""

    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно делать '
                  'отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )

    image = models.ImageField('Фото', upload_to='post_images/', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:50]

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail', args=[self.pk]
        )


class Comment(models.Model):
    """Комментарий."""

    text = models.TextField(
        "Текст",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Номер публикации',
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

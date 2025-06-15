# Create your models here.
from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class CreationInfo(models.Model):
    is_published = models.BooleanField('Опубликовано',
                                       default=True,
                                       help_text='Снимите галочку, '
                                                 'чтобы скрыть публикацию.'
                                       )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Title(models.Model):
    title = models.CharField('Заголовок', max_length=256)

    class Meta:
        abstract = True


class Category(CreationInfo, Title):
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор', unique=True,
                            help_text='Идентификатор страницы для URL; '
                                      'разрешены символы латиницы, цифры, '
                                      'дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(CreationInfo):
    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(CreationInfo, Title):
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата и время публикации',
                                    help_text='Если установить дату и время в '
                                              'будущем — можно делать '
                                              'отложенные публикации.')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор публикации',
                               related_name='post_authors')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name='Местоположение',
        related_name='post_locations'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='post_categories'
    )
    image = models.ImageField(
        'Фото',
        blank=True,
        upload_to='post_images'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title

    @property
    def comment_count(self):
        return self.comment_posts.count()


class Comment(CreationInfo):
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comment_authors'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comment_posts'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'Post {self.post.id}: '
                f'{self.author.first_name} {self.author.last_name}')

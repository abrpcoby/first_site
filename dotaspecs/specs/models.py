import os
from uuid import uuid4

from django.utils.deconstruct import deconstructible
from users.models import User
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from modules.services.utils import image_compress


# def path_and_rename(path):
#     def wrapper(instance, filename):
#         ext = filename.split(".")[-1]
#         filename = "{}.{}".format(uuid4().hex, ext)
#         return os.path.join(path, filename)
#
#     return wrapper


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)


class Specs(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    author = models.CharField(max_length=50, verbose_name="Автор", blank=True)
    description = CKEditor5Field(verbose_name='Описание', config_name='extends')
    content = CKEditor5Field(verbose_name='Текст', config_name='extends')
    image = models.ImageField(upload_to=PathAndRename("images"), blank=True, verbose_name="Картинка")
    file = models.FileField(upload_to='files', null=True, blank=True, verbose_name="Видео")
    view_preview_post = models.BooleanField(default=False, verbose_name="Показывать превью в конце поста")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(default=True, verbose_name="Статус публикации")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, verbose_name="Категории")
    tags = TaggableManager(blank=True)
    moderator_nickname = models.ForeignKey(User, blank=True, null=True,
                                           on_delete=models.SET_NULL, verbose_name="Модератор")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__image = self.image if self.pk else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.__image != self.image and self.image:
            image_compress(self.image.path, width=900, height=900)

    def __str__(self):
        title = f'DotaSpecs | {self.title}'
        return title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    class Meta:
        verbose_name = "Контент"
        verbose_name_plural = "Контент"
        ordering = ['-time_create']


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"
        ordering = ['id']


class AddSpec(models.Model):
    nickname = models.CharField(blank=True, null=True, max_length=100, verbose_name="Автор")
    content = models.TextField(verbose_name="Предложение")
    image = models.ImageField(blank=True, verbose_name="Изображение")
    video = models.FileField(blank=True, null=True, verbose_name="Видео")
    cat = models.CharField(max_length=30, blank=True, null=True, verbose_name="Категория")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Время")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__image = self.image if self.pk else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.__image != self.image and self.image:
            image_compress(self.image.path, width=600, height=600)

    def __str__(self):
        return str(self.nickname)

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"
        ordering = ['time']

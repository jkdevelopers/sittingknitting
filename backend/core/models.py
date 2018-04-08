from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.shortcuts import reverse
from django.db import models
from jsonfield import JSONField
from .utils import build_component, Choices

__all__ = [
    'User',
    'Component',
    'Category',
    'Product',
]


class Component(models.Model):
    uid = models.CharField('UID', max_length=100, blank=False, unique=True)
    template = models.CharField('Шаблон', max_length=100, blank=False)
    name = models.CharField('Название', max_length=100, blank=True, default='')
    attributes = JSONField('Атрибуты', blank=True, default=dict)

    class Meta:
        verbose_name = 'Компонент'
        verbose_name_plural = 'Конпоненты'

    def __str__(self): return 'Компонент "%s"' % (self.name or self.template)

    def save(self, **kwargs):
        if not self.pk: build_component(self, kwargs.pop('context', None))
        return super(Component, self).save(**kwargs)


class User(AbstractUser):
    username = property(lambda self: self.email)
    email = models.EmailField('Email', unique=True)
    address = models.CharField('Адрес', max_length=512, blank=True, default='')
    phone = models.CharField('Телефон', max_length=18, blank=True, default='', validators=[
        RegexValidator(
            regex='\+7 \([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}',
            message='Введите номер телефона в формате +7 (XXX) XXX-XX-XX',
            code='invalid_length_phone',
        ),
    ])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Category(models.Model):
    TYPES = Choices('Основная', 'Вложенная')

    type = models.CharField('Тип', max_length=1, choices=TYPES)
    name = models.CharField('Название', max_length=512)
    parent = models.ForeignKey(
        'self', verbose_name='Родительская категория', related_name='children',
        on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self): return self.name


class Product(models.Model):
    vendor = models.CharField('Артикул', max_length=100, unique=True)
    name = models.CharField('Название', max_length=512, default='')
    brand = models.CharField('Бренд', max_length=100, blank=True, default='')
    photo = models.ImageField('Фотография', upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(
        Category, verbose_name='Категория / подкатегория', related_name='products',
        on_delete=models.CASCADE, blank=True, null=True
    )
    active = models.BooleanField('Показывать на сайте', default=True)
    description = models.TextField('Описание', blank=True, default='')

    quantity = models.PositiveIntegerField('Количество', default=0)
    price = models.PositiveIntegerField('Цена', default=0)
    old_price = models.PositiveIntegerField('Старая цена', blank=True, null=True)
    discount = models.BooleanField('Пометка "акция"', default=False)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    __str__ = lambda self: 'Товар "%s"' % self.name
    get_absolute_url = lambda self: reverse('product', kwargs={'pk': self.pk})

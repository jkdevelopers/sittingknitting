from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, EmailField
from django.core.validators import RegexValidator
from jsonfield import JSONField
from .utils import build_component


__all__ = [
    'Component',
    'User',
]


class Component(Model):
    uid = CharField('UID', max_length=100, blank=False, unique=True)
    template = CharField('Шаблон', max_length=100, blank=False)
    name = CharField('Название', max_length=100, blank=True, default='')
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
    email = EmailField('Email', unique=True)
    address = CharField('Адрес', max_length=512, blank=True, default='')
    phone = CharField('Телефон', max_length=18, blank=True, default='', validators=[
        RegexValidator(
            regex='\+7 \([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}',
            message='Введите номер телефона в формате +7 (XXX) XXX-XX-XX',
            code='invalid_length_phone',
        ),
    ])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

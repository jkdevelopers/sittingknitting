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
    'Subscription',
    'OrderItem',
    'Order',
]

PhoneField = lambda **kwargs: models.CharField('Телефон', max_length=18, validators=[
    RegexValidator(
        regex='\+7 \([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}',
        message='Введите номер телефона в формате +7 (XXX) XXX-XX-XX',
        code='invalid_length_phone',
    ),
], **kwargs)


class Component(models.Model):
    uid = models.CharField('UID', max_length=100, blank=False, unique=True)
    template = models.CharField('Шаблон', max_length=100, blank=False)
    name = models.CharField('Название', max_length=100, blank=True, default='')
    attributes = JSONField('Атрибуты', blank=True, default=dict)

    class Meta:
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'

    def __str__(self): return 'Компонент "%s"' % (self.name or self.template)

    def save(self, **kwargs):
        if not self.pk: build_component(self, kwargs.pop('context', None))
        return super(Component, self).save(**kwargs)


class User(AbstractUser):
    username = property(lambda self: self.email)
    email = models.EmailField('Email', unique=True)
    address = models.CharField('Адрес', max_length=512, blank=True, default='')
    phone = PhoneField(blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Category(models.Model):
    TYPES = Choices(('MAIN', 'Основная'), ('SUB', 'Вложенная'))

    type = models.CharField('Тип', max_length=1, choices=TYPES)
    name = models.CharField('Название', max_length=512)
    parent = models.ForeignKey(
        'self', verbose_name='Родительская категория', related_name='children',
        on_delete=models.CASCADE, blank=True, null=True
    )

    @property
    def level(self):
        if self.type == self.TYPES.MAIN: return 0
        if not self.parent: return -1
        return self.parent.level + 1

    @classmethod
    def get_level(cls, level):
        all = Category.objects.all()
        return [i for i in all if i.level == level]

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self): return self.name

    def save(self, **kwargs):
        if self.pk: return super(Category, self).save(**kwargs)
        ret = super(Category, self).save(**kwargs)
        all_components = Component.objects.all()
        check = lambda pk: [i for i in all_components if i.attributes.get('category') == pk]
        if check(self.pk): return ret

        level = self.level
        if self.level in (0, 1, 2):
            name = ('button', 'section', 'subsection')[level]
            template = 'menu_%s.html' % name

            if level != 0:
                parent = check(self.parent.pk)
                if not parent: return ret
                parent = parent[0]
            else:
                parent = Component.objects.get(uid='menu')

            component = Component(template=template, uid='child')
            component.save()
            component.uid = component.name = '%s %s' % (name, component.pk)
            component.attributes['category'] = self.pk
            component.attributes['title']['value'] = self.name
            component.attributes['url']['value'] = '#'  # get_absolute_url
            component.save()

            items = parent.attributes[name + 's']['value']
            if component not in items:
                parent.attributes[name + 's']['value'] = items + [component.pk]
                parent.save()
        return ret


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

    __str__ = lambda self: self.name
    get_absolute_url = lambda self: reverse('product', kwargs={'pk': self.pk})


class Subscription(models.Model):
    email = models.EmailField('Email', unique=True)
    activated = models.DateTimeField('Активирована', auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    __str__ = lambda self: 'Подписка на %s' % self.email


class OrderItem(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField('Количество')

    def price(self): return self.product.price * self.amount
    price.short_description = 'Цена'

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    __str__ = lambda self: '%s x %s = %s руб.' % (self.product, self.amount, self.price())


class Order(models.Model):
    STATUSES = Choices(
        ('PENDING', 'В обработке'),
        ('ACCEPTED', 'Подтвержден'),
        ('DELIVERED', 'Доставлен'),
        ('CANCELLED', 'Отменен'),
    )

    created = models.DateTimeField('Создан', auto_now_add=True)
    status = models.CharField('Статус', max_length=1, choices=STATUSES, default='0')
    items = models.ManyToManyField(OrderItem, verbose_name='Элементы', blank=True)

    phone = PhoneField()
    delivery_date = models.DateField('Дата доставки')
    delivery_type = models.CharField('Способ доставки', max_length=100)
    delivery_address = models.CharField('Адрес доставки', max_length=300)

    def total(self): return sum(i.price() for i in self.items.all())
    total.short_description = 'Сумма'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    __str__ = lambda self: 'Заказ #%s' % self.pk

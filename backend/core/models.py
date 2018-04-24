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
    'Delivery',
    'Coupon',
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

    def all_children(self):
        direct = list(self.children.all())
        return direct + sum((i.all_children() for i in direct), [])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

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
            component.attributes['url']['value'] = reverse('products', kwargs={'pk': self.pk})
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


class Delivery(models.Model):
    title = models.CharField('Название', max_length=100)
    price = models.PositiveIntegerField('Цена')
    free = models.PositiveIntegerField('Бесплатна при заказе от')

    def get_price(self, value): return self.price if value < self.free else 0

    class Meta:
        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставки'

    __str__ = lambda self: self.title


class Coupon(models.Model):
    TYPES = Choices(
        ('PRICE', 'Сумма'),
        ('PERCENT', 'Процент'),
    )

    type = models.CharField('Тип', max_length=1, choices=TYPES)
    value = models.PositiveIntegerField('Значение (руб или %)')
    code = models.CharField('Код', max_length=10)
    active = models.BooleanField('Активен', default=True)

    def get_discount(self, total):
        if self.type == self.TYPES.PRICE:
            return max(0, total - self.value)
        elif self.type == self.TYPES.PERCENT:
            return max(0, int(total - total / 100 * self.value))

    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'

    __str__ = lambda self: 'Купон на %s%s' % (self.value, ' руб.' if self.type == self.TYPES.PRICE else '%')


class Order(models.Model):
    STATUSES = Choices(
        ('PENDING', 'В обработке'),
        ('ACCEPTED', 'Подтвержден'),
        ('DELIVERED', 'Доставлен'),
        ('CANCELLED', 'Отменен'),
    )

    manager = models.ForeignKey(User, models.SET_NULL, verbose_name='Менеджер', blank=True, null=True)
    created = models.DateTimeField('Создан', auto_now_add=True)
    status = models.CharField('Статус', max_length=1, choices=STATUSES, default='0')
    items = models.ManyToManyField(OrderItem, verbose_name='Элементы', blank=True)
    coupon = models.ForeignKey(Coupon, models.SET_NULL, verbose_name='Купон', blank=True, null=True)

    phone = PhoneField()
    delivery_date = models.DateField('Дата доставки', blank=True, null=True)
    delivery_type = models.ForeignKey(Delivery, models.SET_NULL, verbose_name='Способ доставки', blank=True, null=True)
    delivery_address = models.CharField('Адрес доставки', max_length=300, blank=True, default='')
    correction = models.IntegerField('Корректировка суммы', default=0)

    def items_total(self): return sum(i.price() for i in self.items.all())
    items_total.short_description = 'Стоимость товаров'

    def discount(self):
        if self.coupon is None: return 0
        return self.coupon.get_discount(self.items_total())
    discount.short_description = 'Скидка'

    def delivery_price(self):
        if self.delivery_type is None: return 0
        return self.delivery_type.get_price(self.items_total())
    delivery_price.short_description = 'Стоимость доставки'

    def total(self): return self.items_total() + self.delivery_price() - self.discount() + self.correction
    total.short_description = 'Итого'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    __str__ = lambda self: 'Заказ #%s' % self.pk

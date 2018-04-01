from django.db.models import Model, CharField, BooleanField
from .utils import build_component
from jsonfield import JSONField

__all__ = [
    'Component',
]


class Component(Model):
    uid = CharField('UID', max_length=100, blank=False)
    template = CharField('Template', max_length=100, blank=False)
    modification = CharField('Modification', max_length=100, blank=False)
    name = CharField('Name', max_length=100, blank=True, default='')
    attributes = JSONField('Attributes', blank=True, default=dict)

    class Meta:
        verbose_name = 'Component'
        verbose_name_plural = 'Components'

    def __str__(self): return 'Component "%s"' % (self.name or self.template)

    def save(self, **kwargs):
        if not self.pk: build_component(self)
        return super(Component, self).save(**kwargs)

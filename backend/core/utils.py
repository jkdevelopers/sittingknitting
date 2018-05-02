from sorl.thumbnail.shortcuts import get_thumbnail
from voluptuous import Schema, Optional, Any
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from os.path import relpath
from django.conf import settings
from django.forms import fields

COMPONENTS_PREFIX = relpath(
    str(settings.COMPONENTS_DIR),
    str(settings.TEMPLATES_DIR)
)


class Choices:
    def __init__(self, *values):
        self.choices = {}
        for i, value in enumerate(values):
            db_value = str(i)
            const_value = value
            if isinstance(value, tuple):
                const_value, value = value
            self.choices[db_value] = value
            attr = slugify(const_value).replace('-', '_').upper()
            setattr(self, attr, db_value)

    def __iter__(self):
        items = sorted(self.choices.items(), key=lambda x: x[0])
        for i in items: yield i

    def __getitem__(self, item):
        return self.choices[item]


class Attribute:
    attr_type = 'attribute'
    field_type = fields.Field
    value_scheme = Schema(object)
    value_default = None
    data_scheme = Schema({})

    def __init__(self, **data):
        data = {key: value for key, value in data.items() if value is not None}
        self.context = data.pop('context', {})
        self.name = data.pop('name')
        self.id = data.pop('id')
        self.default = data.pop('default', self.value_default)
        value = data.pop('value', self.default)
        self.value = self.value_scheme(value)
        self.data = self.data_scheme(data)
        self.context[self.id + '_value'] = self.value

    def render(self): return str(self.value)

    def field(self):
        return self.field_type(
            label=self.name,
            initial=self.value,
            required=False
        )

    def parse(self, form):
        field = form.fields[self.id]
        value = form.cleaned_data[self.id]
        self.value = field.clean(value)

    def serialize(self):
        return {
            'name': self.name,
            'type': self.attr_type,
            'value': self.value,
            'default': self.default,
            'data': self.data,
        }


class Text(Attribute):
    attr_type = 'text'
    field_type = fields.CharField
    value_scheme = Schema(str)
    value_default = ''
    data_scheme = Schema({})


class Image(Attribute):
    attr_type = 'image'
    field_type = fields.ImageField
    value_scheme = Schema(str)
    value_default = ''
    data_scheme = Schema({
        Optional('width'): Any(int, float, str),
        Optional('height'): Any(int, float, str),
    })

    def render(self):
        if not self.value: return ''
        width = self.data.get('width', '')
        height = self.data.get('height', '')
        if not width and not height:
            return default_storage.url(self.value)
        else:
            size = '%sx%s' % (width, height)
            image = get_thumbnail(self.value, size, crop='center')
            return image.url

    def field(self):
        field = super(Image, self).field()
        field.upload_to = 'images'
        if self.value:
            url = default_storage.url(self.value)
            mock = type('', (), {'url': url, '__str__': lambda _: self.value})
            field.initial = mock
        return field

    def parse(self, form):
        field = form.fields[self.id]
        value = form.cleaned_data[self.id]
        if not value:
            if value is None: return
            default_storage.delete(self.value)
            self.value = ''
        else:
            changed = not field.initial or field.initial.url != value.url
            if not changed: return
            file = field.clean(value)
            filename = default_storage.save(file.name, file)
            self.value = filename


class Boolean(Attribute):
    attr_type = 'boolean'
    field_type = fields.BooleanField
    value_scheme = Schema(bool)
    value_default = False
    data_scheme = Schema({Optional('states'): [str, str]})

    def render(self):
        states = self.data.get('states')
        if states is None:
            self.context[self.id] = self.value
            return ''
        return self.data['states'][not self.value]


class Number(Attribute):
    attr_type = 'number'
    field_type = fields.IntegerField
    value_scheme = Schema(int)
    value_default = 0
    data_scheme = Schema({Optional('min'): int, Optional('max'): int})

    def field(self):
        field = super(Number, self).field()
        if 'min' in self.data: field.min_value = self.data['min']
        if 'max' in self.data: field.max_value = self.data['max']
        return field


class List(Attribute):
    attr_type = 'list'
    field_type = fields.CharField
    value_scheme = Schema(list)
    value_default = []
    data_scheme = Schema({'component': str, Optional('fake'): bool})

    def __init__(self, **data):
        from .models import Component
        super(List, self).__init__(**data)
        self.components = [Component.objects.get(pk=pk) for pk in self.value]
        self.context['list_%s_empty' % self.id] = not bool(self.components)

    def render(self):
        if self.data.get('fake'): return ''
        from .tags import component
        return mark_safe('\n'.join(component(
            self.context,
            comp.template,
            comp.uid
        ) for comp in self.components))

    def field(self):
        return self.field_type(
            label=self.name,
            initial=';'.join('%s:%s' % (comp.pk, comp.name) for comp in self.components),
            widget=fields.TextInput(attrs={
                'data-list': 'true',
                'data-template': self.data['component'],
            }),
            required=False,
        )

    def parse(self, form):
        field = form.fields[self.id]
        raw_value = form.cleaned_data[self.id]
        value = field.clean(raw_value)
        self.value = [int(i.split(':')[0]) for i in value.split(';') if i]


ATTRIBUTES = {attr.attr_type: attr for attr in [
    Attribute,
    Text,
    Image,
    Boolean,
    Number,
    List,
]}


def build_component(component, context=None):
    component.name = component.uid
    path = COMPONENTS_PREFIX + '/' + component.template
    template = get_template(path)
    context = context or {}
    context['__collected'] = {}
    template.render(context)
    attributes = context['__collected']
    component.attributes = attributes


def build_attributes(component):
    attributes = []
    for id, data in component.attributes.items():
        if type(data) != dict or 'type' not in data: continue
        name = data['name']
        value = data['value']
        attr_data = data['data']
        Class = ATTRIBUTES[data['type']]
        attributes.append(Class(
            id=id,
            name=name,
            value=value,
            **attr_data
        ))
    return attributes


def get_object_safe(klass, *args, default=None, error=None, **kwargs):
    try:
        object = klass.objects.get(*args, **kwargs)
        return object
    except ObjectDoesNotExist:
        if error is not None: raise error
        return default

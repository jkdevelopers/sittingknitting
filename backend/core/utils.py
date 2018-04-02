from voluptuous import Schema, Any, DefaultTo as Default, Optional, ALLOW_EXTRA
from django.core.files.storage import default_storage
from django.template.loader import get_template
from os.path import relpath
from django.conf import settings
from django.forms import fields

COMPONENTS_PREFIX = relpath(
    str(settings.COMPONENTS_DIR),
    str(settings.TEMPLATES_DIR)
)


class Attribute:
    type = 'attribute'
    field_type = fields.Field
    value_scheme = Schema(object)
    attrs_scheme = Schema({}, extra=ALLOW_EXTRA)

    def __init__(self, context, name, id, value=None, **attrs):
        self.context = context
        self.name = name
        self.id = id
        self.value = self.value_scheme(value)
        self.attrs = self.attrs_scheme(attrs)

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
            'type': self.type,
            'value': self.value,
            'attrs': self.attrs,
        }


class Text(Attribute):
    type = 'text'
    field_type = fields.CharField
    value_scheme = Schema(Any(str, Default('')))
    attrs_scheme = Schema({})


class Image(Attribute):
    type = 'image'
    field_type = fields.ImageField
    value_scheme = Schema(Any(str, Default('')))
    attrs_scheme = Schema({})

    def render(self):
        if not self.value: return ''
        return default_storage.url(self.value)

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
    type = 'boolean'
    field_type = fields.BooleanField
    value_scheme = Schema(Any(bool, Default(True)))
    attrs_scheme = Schema({Optional('states'): [str, str]})

    def render(self):
        states = self.attrs.get('states')
        if states is None:
            self.context[self.id] = self.value
            return ''
        return self.attrs['states'][not self.value]


class Number(Attribute):
    type = 'number'
    field_type = fields.IntegerField
    value_scheme = Schema(Any(int, Default(0)))
    attrs_scheme = Schema({Optional('min'): int, Optional('max'): int})

    def field(self):
        field = super(Number, self).field()
        if 'min' in self.attrs: field.min_value = self.attrs['min']
        if 'max' in self.attrs: field.max_value = self.attrs['max']
        return field


ATTRIBUTES = {attr.type: attr for attr in [
    Attribute,
    Text,
    Image,
    Boolean,
    Number,
]}


def build_component(component):
    component.name = component.uid
    path = COMPONENTS_PREFIX + '/' + component.template
    template = get_template(path)
    context = {'__collected': {}}
    template.render(context)
    attributes = context['__collected']
    component.attributes = attributes


def build_attributes(component):
    attributes = []
    for id, data in component.attributes.items():
        name = data['name']
        value = data['value']
        attrs = data['attrs']
        Class = ATTRIBUTES[data['type']]
        attributes.append(Class({}, name, id, value, **attrs))
    return attributes

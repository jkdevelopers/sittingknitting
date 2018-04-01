from voluptuous import Schema, Any, DefaultTo as Default, ALLOW_EXTRA
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

    def __init__(self, name, id, value=None, **attrs):
        self.name = name
        self.id = id
        self.value = self.value_scheme(value)
        self.attrs = self.attrs_scheme(attrs)

    def render(self): raise NotImplementedError

    def field(self):
        return self.field_type(
            label=self.name,
            initial=self.value,
            required=False
        )

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
    value_scheme = Schema(Any(str, Default('Sample text')))
    attrs_scheme = Schema({})

    def render(self): return self.value


ATTRIBUTES = {attr.type: attr for attr in [
    Attribute,
    Text,
]}


def build_component(component):
    component.name = 'Component "%s"' % component.template
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
        attributes.append(Class(name, id, value, **attrs))
    return attributes

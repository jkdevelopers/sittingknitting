from django.template.loader import get_template
from django.template import Template, Library
from django.utils.safestring import mark_safe
from .models import Component
from .utils import ATTRIBUTES, COMPONENTS_PREFIX

register = Library()


@register.simple_tag(takes_context=True)
def edit(context, mode):
    if mode not in ('on', 'enable', True): return ''
    if not context['request'].user.is_staff: return ''
    context['__edit'] = True
    return ''


@register.simple_tag(takes_context=True)
def modification(context, name):
    if type(name) != str: raise RuntimeError('Modification name must be a string')
    if not name: raise RuntimeError('Empty modification name')
    context['__modification'] = name
    return ''


@register.simple_tag(takes_context=True)
def component(context, template, id=None):
    if id is None: raise RuntimeError('Component ID is currently required')
    modification = context.get('__modification', 'main')
    component, _ = Component.objects.get_or_create(template=template, modification=modification, uid=id)
    template = get_template(COMPONENTS_PREFIX + '/' + component.template)
    context['__attributes'] = component.attributes
    rendered = template.render(context.flatten())
    print(context.get('__edit'))
    if context.get('__edit') is None: return rendered
    wrapper = '<div data-component="%s" sytle="display: inherit">%%s</div>' % component.pk
    return mark_safe(wrapper % rendered)


@register.simple_tag(takes_context=True)
def attribute(context, name=None, type=None, id=None, **attrs):
    if type is None: raise RuntimeError('Component type is required')
    if id is None: raise RuntimeError('Component ID is currently required')
    if type not in ATTRIBUTES: raise RuntimeError('No such attribute type')
    attributes = context.get('__attributes')
    collected = context.get('__collected')
    if collected is not None:
        value = None
    else:
        if attributes is None: raise RuntimeError('No component data found')
        if id not in attributes: raise RuntimeError('No attribute data found')
        value = context['__attributes'][id]['value']
    if name is None: name = type.title()
    attribute = ATTRIBUTES[type](name, id, value, **attrs)
    if collected is not None: collected[id] = attribute.serialize()
    return attribute.render()

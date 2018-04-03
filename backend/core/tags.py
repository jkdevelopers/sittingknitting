from django.template.loader import get_template
from django.template import Library
from django.utils.safestring import mark_safe
from .models import Component
from .utils import ATTRIBUTES, COMPONENTS_PREFIX

register = Library()


@register.simple_tag(takes_context=True)
def component(context, template, id=None, **kwargs):
    if id is None: raise RuntimeError('Component ID is currently required')
    component, _ = Component.objects.get_or_create(template=template, uid=id)
    template = get_template(COMPONENTS_PREFIX + '/' + component.template)
    context['__attributes'] = component.attributes
    context.update(kwargs)
    rendered = template.render(context.flatten())
    if context.get('edit_mode') is None: return rendered
    wrapper = '<div data-component="%s">%%s</div>' % component.pk
    return mark_safe(wrapper % rendered)


@register.simple_tag(takes_context=True)
def attribute(context, name=None, type=None, id=None, **data):
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
    attribute = ATTRIBUTES[type](
        id=id,
        name=name,
        value=value,
        context=context,
        **data
    )
    if collected is not None: collected[id] = attribute.serialize()
    return attribute.render()

from django.forms import ModelForm
from .utils import build_attributes
from .models import Component


class ComponentForm(ModelForm):
    class Meta:
        model = Component
        fields = []

    def __init__(self, **kwargs):
        super(ComponentForm, self).__init__(**kwargs)
        self.attributes = build_attributes(kwargs['instance'])
        for attr in self.attributes: self.fields[attr.id] = attr.field()

    def clean(self):
        return super(ComponentForm, self).clean()

    def save(self, commit=True):
        for attr in self.attributes:
            field = self.fields[attr.id]
            value = self.cleaned_data[attr.id]
            attr.value = field.clean(value)
        attributes = {attr.id: attr.serialize() for attr in self.attributes}
        self.instance.attributes = attributes
        return super(ComponentForm, self).save(commit=commit)

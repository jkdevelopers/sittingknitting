from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
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
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('save', 'Save'))
        self.helper.form_tag = False

    def save(self, commit=True):
        for attr in self.attributes: attr.parse(self)
        attributes = {attr.id: attr.serialize() for attr in self.attributes}
        self.instance.attributes = attributes
        return super(ComponentForm, self).save(commit=commit)

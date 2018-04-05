from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .utils import build_attributes
from .models import *

__all__ = [
    'ComponentForm',
    'RegisterForm',
]


class ComponentForm(ModelForm):
    class Meta:
        model = Component
        fields = ['name']

    def __init__(self, **kwargs):
        super(ComponentForm, self).__init__(**kwargs)
        self.fields['name'].label = 'Component name'
        self.attributes = build_attributes(kwargs['instance'])
        for attr in self.attributes: self.fields[attr.id] = attr.field()
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('save', 'Save', css_class='btn-block'))
        self.helper.form_tag = False

    def save(self, commit=True):
        for attr in self.attributes: attr.parse(self)
        attributes = {attr.id: attr.serialize() for attr in self.attributes}
        self.instance.attributes = attributes
        return super(ComponentForm, self).save(commit=commit)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label

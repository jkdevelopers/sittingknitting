from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from .utils import build_attributes
from .models import *

__all__ = [
    'ComponentForm',
    'RegisterForm',
    'SubscriptionForm',
    'FeedbackForm',
]


class ComponentForm(forms.ModelForm):
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


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']


class FeedbackForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=200)
    phone = forms.RegexField(
        '\+7 \([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}',
        label='Телефон',
        error_messages={'invalid': 'Введите корректный номер телефона'},
        required=False
    )
    email = forms.EmailField(label='Email', required=False)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea)

    def clean(self):
        data = super(FeedbackForm, self).clean()
        if not self.is_valid(): return data
        if not data['phone'] and not data['email']:
            raise forms.ValidationError('Укажите телефон или email для обратной связи')
        return data

from django.views.generic import UpdateView
from django.shortcuts import reverse
from .models import Component
from .forms import ComponentForm


class ComponentEditView(UpdateView):
    model = Component
    form_class = ComponentForm
    template_name = 'core/component.html'
    success_url = '.'


component_edit = ComponentEditView.as_view()

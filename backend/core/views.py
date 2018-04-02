from django.views.generic import UpdateView
from django.contrib import messages
from django.shortcuts import reverse
from django.http import Http404
from .models import Component
from .forms import ComponentForm


class ComponentEditView(UpdateView):
    model = Component
    form_class = ComponentForm
    template_name = 'core/component.html'
    success_url = '.'

    def form_valid(self, form):
        messages.success(self.request, 'Component updated')
        return super(ComponentEditView, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_staff: raise Http404
        return super(ComponentEditView, self).dispatch(*args, **kwargs)


component_edit = ComponentEditView.as_view()

from django.views.generic import UpdateView, TemplateView, View
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.http import Http404, HttpResponse
from .models import Component
from .forms import ComponentForm

__all__ = [
    'home',
    'component_edit',
    'component_action',
    'login',
    'logout',
]


class EditableView(TemplateView):
    cache_timeout = 60 * 15

    def dispatch(self, *args, **kwargs):
        staff = self.request.user.is_staff
        edit = self.request.GET.get('edit')
        if staff and edit is not None:
            state = edit in ('true', 'on', 'enabled')
            self.request.session['edit_mode'] = state
        return super(EditableView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        staff = self.request.user.is_staff
        edit = self.request.session.get('edit_mode')
        if staff and edit: kwargs['edit_mode'] = True
        return super(EditableView, self).get_context_data(**kwargs)


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


class ComponentActionView(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_staff: raise Http404
        return super(ComponentActionView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        action = self.request.GET.get('action')
        if action is None: raise Http404
        if action == 'create':
            template = self.request.GET.get('template')
            if template is None: raise Http404
            component = Component(template=template, uid='child')
            component.save()
            component.uid = 'child ' + str(component.pk)
            component.name = component.uid
            component.save()
            return HttpResponse(str(component.pk))
        elif action == 'remove':
            pk = self.request.GET.get('pk')
            if pk is None: raise Http404
            component = Component.objects.get(pk=int(pk))
            component.delete()
            return HttpResponse('OK')
        raise Http404


class LoginView(auth_views.LoginView):
    def get(self, *args, **kwargs): raise Http404

    def form_valid(self, form):
        ret = super(LoginView, self).form_valid(form)
        user = form.get_user()
        messages.success(self.request, 'Logged in as "%s"' % user.username);
        return ret


class LogoutView(auth_views.LogoutView):
    def dispatch(self, *args, **kwargs):
        messages.success(self.request, 'Logged out')
        return super(LogoutView, self).dispatch(*args, **kwargs)


home = EditableView.as_view(template_name='home.html')
component_edit = ComponentEditView.as_view()
component_action = ComponentActionView.as_view()
login = LoginView.as_view()
logout = LogoutView.as_view()

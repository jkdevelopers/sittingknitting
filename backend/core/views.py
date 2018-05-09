from django.contrib.auth import views as auth_views, login as auth_login
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.views import generic
from django.db.models import Q
from re import fullmatch
from .models import *
from .forms import *

__all__ = [
    'home',
    'component_edit',
    'component_action',
    'login',
    'logout',
    'register',
    'subscribe',
    'product',
    'products',
    'cart_action',
    'cart',
]


class EditableMixin:
    def dispatch(self, *args, **kwargs):
        staff = self.request.user.is_staff
        edit = self.request.GET.get('edit')
        if staff and edit is not None:
            state = edit in ('true', 'on', 'enabled')
            self.request.session['edit_mode'] = state
        return super(EditableMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        staff = self.request.user.is_staff
        edit = self.request.session.get('edit_mode')
        if staff and edit: kwargs['edit_mode'] = True
        return super(EditableMixin, self).get_context_data(**kwargs)


class HomeView(EditableMixin, generic.TemplateView):
    template_name = 'pages/home.html'


class ComponentEditView(generic.UpdateView):
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


class ComponentActionView(generic.View):
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
    success_url = reverse_lazy('home')

    def get(self, *args, **kwargs):
        return redirect(reverse_lazy('register'))

    def form_valid(self, form):
        ret = super(LoginView, self).form_valid(form)
        user = form.get_user()
        # messages.success(self.request, 'Logged in as "%s"' % user.username)
        return ret

    def form_invalid(self, form): return redirect(self.get_success_url())


class LogoutView(auth_views.LogoutView):
    success_url = reverse_lazy('home')

    def dispatch(self, *args, **kwargs):
        # messages.success(self.request, 'Logged out')
        return super(LogoutView, self).dispatch(*args, **kwargs)


class RegisterView(EditableMixin, generic.FormView):
    form_class = RegisterForm
    template_name = 'pages/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(self.request, user)
        return super(RegisterView, self).form_valid(form)


class SubscribeView(generic.CreateView):
    form_class = SubscriptionForm
    success_url = reverse_lazy('home')

    def form_invalid(self, form):
        return HttpResponse(str(form.errors['email']))

    def form_valid(self, form):
        super(SubscribeView, self).form_valid(form)
        return HttpResponse('OK')


class ProductView(EditableMixin, generic.DetailView):
    model = Product
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        related = Product.objects.filter(category=self.object.category).exclude(pk=self.object.pk)
        kwargs['related'] = related
        return super(ProductView, self).get_context_data(**kwargs)


class ProductsView(EditableMixin, generic.ListView):
    model = Product
    template_name = 'pages/products.html'
    context_object_name = 'products'

    def get(self, *args, **kwargs):
        pk = kwargs.get('pk')
        self.category = None
        if pk is not None:
            category = get_object_or_404(Category, pk=pk)
            self.category = category
        self.search = self.request.GET.get('search')
        return super(ProductsView, self).get(*args, **kwargs)

    def get_queryset(self):
        qs = Product.objects.filter(active=True, quantity__gt=0)
        if self.search is not None:
            return qs.filter(
                Q(name__icontains=self.search) |
                Q(vendor__icontains=self.search) |
                Q(brand__icontains=self.search)
            )
        if self.category is None: return qs
        qs = qs.filter(category__isnull=False)
        categories = [self.category] + self.category.all_children()
        return list(filter(lambda x: x.category in categories, qs))

    def get_context_data(self, **kwargs):
        kwargs = super(ProductsView, self).get_context_data(**kwargs)
        kwargs['current'] = self.category
        kwargs['search'] = self.search
        kwargs['count'] = len(self.object_list)

        GROUPS = [
            ('root', 'root'),
            ('category', 'categories'),
            ('subcategory', 'subcategories'),
        ]

        for level, (name, plural) in enumerate(GROUPS):
            kwargs[plural] = Category.get_level(level)
            key = name + '_active'
            kwargs[key] = None
            if self.category is None: continue
            if self.category.level == level:
                kwargs[key] = self.category
            else:
                temp = [i for i in kwargs[plural] if self.category in i.all_children()]
                if temp: kwargs[key] = temp[0]

        return kwargs


class CartActionView(generic.View):
    def dispatch(self, *args, **kwargs):
        action = kwargs.get('action')
        data = kwargs.get('data')
        if data is not None:
            if action == 'add': self.add(data)
            elif action == 'remove': self.remove(data)
            elif action == 'delivery': self.delivery(data)
            elif action == 'add-coupon': self.add_coupon(data)
            elif action == 'remove-coupon': self.remove_coupon()
            elif action == 'place-order': self.place_order()
        url = self.request.META.get('HTTP_REFERER', '/')
        return redirect(url)

    def add(self, data):
        if not data.isdigit(): return
        data = int(data)
        product = get_object_or_404(Product, pk=data)
        if not product.active or product.quantity == 0: return
        items = set(self.request.session.get('cart', []))
        items.add(data)
        self.request.session['cart'] = list(items)

    def remove(self, data):
        if not data.isdigit(): return
        data = int(data)
        items = set(self.request.session.get('cart', []))
        items.remove(data)
        self.request.session['cart'] = list(items)

    def delivery(self, data):
        if not data.isdigit(): return
        data = int(data)
        delivery = get_object_or_404(Delivery, pk=data)
        self.request.session['delivery'] = delivery.pk

    def add_coupon(self, data):
        coupons = list(Coupon.objects.filter(code=data))
        if not coupons:
            messages.error(self.request, 'Такого купона не существует')
            return
        self.request.session['coupon'] = coupons[0].pk

    def remove_coupon(self): del self.request.session['coupon']

    def place_order(self):
        cart = self.request.session.get('cart', [])
        products = list(Product.objects.filter(pk__in=cart, active=True, quantity__gt=0))
        coupon = self.request.session.get('coupon', None)
        delivery = self.request.session.get('delivery', None)
        phone = self.request.POST.get('phone')

        if not products: messages.error(self.request, 'Ваша корзина пуста'); return
        if not delivery: messages.error(self.request, 'Пожалуйста, выберите способ доставки'); return
        if not phone: messages.error(self.request, 'Пожалуйста, ведите контактный телефон'); return
        if not fullmatch('\+7 \([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}', phone):
            messages.error(self.request, 'Пожалуйста, введите корректный номер телефона'); return

        items = [OrderItem(product=i, amount=1) for i in products]
        for i in items: i.save()
        order = Order(
            phone=phone,
            coupon=coupon and get_object_or_404(Coupon, pk=coupon),
            delivery_type=get_object_or_404(Delivery, pk=delivery),
        )
        order.save()
        order.items.set(items)
        order.save()
        order.update()
        messages.success(self.request, 'Заказ успешно создан. Номер заказа: {:03}'.format(order.pk))


class CartView(generic.TemplateView):
    template_name = 'pages/cart.html'

    def get_context_data(self, **kwargs):
        cart = self.request.session.get('cart', [])
        products = Product.objects.filter(pk__in=cart, active=True, quantity__gt=0)
        coupon = self.request.session.get('coupon', None)
        delivery = self.request.session.get('delivery', None)
        order = Order(
            coupon=coupon and get_object_or_404(Coupon, pk=coupon),
            delivery_type=delivery and get_object_or_404(Delivery, pk=delivery),
        )
        order.items_total = lambda: sum(i.price for i in products)
        kwargs['order'] = order
        kwargs['products'] = products
        kwargs['delivery_types'] = [(i.pk, i.title) for i in Delivery.objects.all()]
        return super(CartView, self).get_context_data(**kwargs)


home = HomeView.as_view()
component_edit = ComponentEditView.as_view()
component_action = ComponentActionView.as_view()
login = LoginView.as_view()
logout = LogoutView.as_view()
register = RegisterView.as_view()
subscribe = SubscribeView.as_view()
product = ProductView.as_view()
products = ProductsView.as_view()
cart_action = CartActionView.as_view()
cart = CartView.as_view()

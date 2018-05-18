from django.contrib.auth import views as auth_views, login as auth_login
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.views import generic
from django.db.models import Q
from re import fullmatch
from .utils import get_object_safe
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
    'info',
]


# ---------------------------------------- #
#               CMS SECTION                #
# ---------------------------------------- #


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


# ---------------------------------------- #
#               AUTH SECTION               #
# ---------------------------------------- #


class LoginView(auth_views.LoginView):
    success_url = reverse_lazy('home')

    def get(self, *args, **kwargs):
        return redirect(reverse_lazy('register'))

    def form_valid(self, form):
        ret = super(LoginView, self).form_valid(form)
        user = form.get_user()
        messages.success(self.request, 'Выполнен вход в аккаунт "%s"' % user.username)
        return ret

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка входа в аккаунт')
        return redirect(self.get_success_url())


class LogoutView(auth_views.LogoutView):
    success_url = reverse_lazy('home')

    def dispatch(self, *args, **kwargs):
        messages.success(self.request, 'Вы вышли из аккаунта')
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
        messages.success(self.request, 'Регистрация успешно завершена')
        messages.success(self.request, 'Выполнен вход в аккаунт "%s"' % user.username)
        return super(RegisterView, self).form_valid(form)


# ---------------------------------------- #
#               MISC SECTION               #
# ---------------------------------------- #


class SubscribeView(generic.CreateView):
    form_class = SubscriptionForm
    success_url = reverse_lazy('home')

    def form_invalid(self, form):
        return HttpResponse(str(form.errors['email']))

    def form_valid(self, form):
        super(SubscribeView, self).form_valid(form)
        return HttpResponse('OK')


# ---------------------------------------- #
#              PLAIN SECTION               #
# ---------------------------------------- #


class HomeView(EditableMixin, generic.TemplateView):
    template_name = 'pages/home.html'


class InfoView(EditableMixin, generic.FormView):
    template_name = 'pages/info.html'
    form_class = FeedbackForm

    def form_valid(self, form):
        context = self.get_context_data()
        context['form'] = self.form_class()
        context['form'].success = True
        return self.render_to_response(context)


class ProductView(EditableMixin, generic.DetailView):
    model = Product
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def get_queryset(self): return Product.objects.filter(active=True, show=True)

    def get_context_data(self, **kwargs):
        related = self.get_queryset().filter(category=self.object.category).exclude(pk=self.object.pk)
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
        parse = lambda s: set(int(i) for i in s.split(',') if i.isdigit())
        subs = parse(self.request.GET.get('subs', ''))
        brands = self.request.GET.get('brands', '').split(',')
        self.subs = Category.objects.filter(pk__in=subs)
        self.brands = [i for i in brands if Product.objects.filter(brand=i).count()]
        return super(ProductsView, self).get(*args, **kwargs)

    def get_queryset(self):
        qs = Product.objects.filter(active=True, show=True)
        if self.search is not None:
            return qs.filter(
                Q(name__icontains=self.search) |
                Q(vendor__icontains=self.search) |
                Q(brand__icontains=self.search)
            )
        if self.category is None: return qs
        subs = self.category.recursive()
        qs = qs.filter(category__in=subs)
        if self.subs:
            subs = set.union(*(set(i.pk for i in j.recursive()) for j in self.subs))
            qs = qs.filter(category__pk__in=subs)
        if self.brands: qs = qs.filter(brand__in=self.brands)
        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(ProductsView, self).get_context_data(**kwargs)
        kwargs['root'] = Category.objects.filter(type=Category.TYPES.MAIN)
        kwargs['current'] = self.category
        kwargs['search'] = self.search
        kwargs['count'] = len(self.object_list)
        kwargs['subs'] = self.subs
        kwargs['brands'] = self.brands

        if self.category is None: return kwargs

        categories = self.category.recursive()

        kwargs['all_subs'] = Category.objects.filter(parent=self.category)
        kwargs['all_brands'] = set(Product.objects.filter(category__in=categories).values_list('brand', flat=True))
        # kwargs['all_mods'] = ...

        return kwargs


# ---------------------------------------- #
#               CART SECTION               #
# ---------------------------------------- #


class Cart:
    def __init__(self, session):
        self.session = session
        self.products = session.get('products', [])
        self.coupon = session.get('coupon')
        self.delivery = session.get('delivery')
        self.clean()
        if session.get('total') is None: self.recalc()

    def clean(self):
        if self.products:
            products = []
            for pk in self.products:
                product = get_object_safe(Product, pk=pk, quantity__gt=0)
                if product is not None: products.append(product)
            if len(products) != len(self.products):
                self.session['products'] = [i.pk for i in products]
            self.products = products

        if self.coupon is not None:
            self.coupon = get_object_safe(Coupon, pk=self.coupon)
            if self.coupon is None: del self.session['coupon']

        if self.delivery is not None:
            self.delivery = get_object_safe(Delivery, pk=self.delivery)
            if self.delivery is None: del self.session['delivery']

    def recalc(self):
        order = Order(coupon=self.coupon, delivery_type=self.delivery)
        order.items_total = lambda: sum(i.price for i in self.products)
        self.session['total'] = order.total()

    def add_product(self, pk):
        product = get_object_safe(Product, pk=pk, quantity__gt=0)
        if product is None: return False
        products = [i.pk for i in self.products]
        if pk in products: return False
        self.products.append(product)
        self.session['products'] = [i.pk for i in self.products]
        self.recalc()
        return True

    def remove_product(self, pk):
        products = [i.pk for i in self.products]
        if pk not in products: return False
        index = products.index(pk)
        del self.products[index]
        self.session['products'] = [i.pk for i in self.products]
        self.recalc()
        return True

    def add_coupon(self, code):
        if self.coupon is not None: return True
        coupon = get_object_safe(Coupon, code=code)
        if coupon is None: return False
        self.coupon = coupon
        self.session['coupon'] = self.coupon.pk
        self.recalc()
        return True

    def remove_coupon(self):
        if self.coupon is None: return False
        self.coupon = None
        del self.session['coupon']
        self.recalc()
        return True

    def change_delivery(self, pk):
        delivery = get_object_safe(Delivery, pk=pk)
        if delivery is None: return False
        if self.delivery is not None and pk == self.delivery.pk: return False
        self.delivery = delivery
        self.session['delivery'] = self.delivery.pk
        self.recalc()
        return True


class CartActionView(generic.View):
    def dispatch(self, *args, **kwargs):
        action = kwargs.get('action')
        self.data = kwargs.get('data')
        if self.data is not None:
            self.cart = Cart(self.request.session)
            if action == 'add-coupon':
                if not self.cart.add_coupon(self.data):
                    messages.error(self.request, 'Такого купона не существует')
            elif action == 'remove-coupon': self.cart.remove_coupon()
            elif action == 'place-order': self.place_order()
            if self.data.isdigit():
                if action == 'add': self.cart.add_product(int(self.data))
                elif action == 'remove': self.cart.remove_product(int(self.data))
                elif action == 'delivery': self.cart.change_delivery(int(self.data))
        url = self.request.META.get('HTTP_REFERER', '/')
        return redirect(url)

    def place_order(self):
        phone = self.request.POST.get('phone')
        if not self.cart.products: messages.error(self.request, 'Ваша корзина пуста')
        elif not self.cart.delivery: messages.error(self.request, 'Пожалуйста, выберите способ доставки')
        elif not phone: messages.error(self.request, 'Пожалуйста, введите контактный телефон')
        elif not fullmatch('\+7 \([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}', phone):
            messages.error(self.request, 'Пожалуйста, введите корректный номер телефона')
        else:
            items = [OrderItem(product=i, amount=1) for i in self.cart.products]
            for i in items: i.save()
            order = Order(phone=phone, coupon=self.cart.coupon, delivery_type=self.cart.delivery)
            order.save()
            order.items.set(items)
            order.save()
            order.update()
            self.cart.recalc()
            messages.success(self.request, 'Заказ успешно создан. Номер заказа: {:03}'.format(order.pk))


class CartView(generic.TemplateView):
    template_name = 'pages/cart.html'

    def get_context_data(self, **kwargs):
        cart = Cart(self.request.session)
        order = Order(coupon=cart.coupon, delivery_type=cart.delivery)
        order.items_total = lambda: sum(i.price for i in cart.products)
        kwargs['order'] = order
        kwargs['products'] = cart.products
        kwargs['delivery_types'] = [(i.pk, i.title) for i in Delivery.objects.all()]
        return super(CartView, self).get_context_data(**kwargs)


# ---------------------------------------- #
#             BINDINGS SECTION             #
# ---------------------------------------- #


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
info = InfoView.as_view()

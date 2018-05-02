from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .utils import get_object_safe
from django.contrib import admin
from .models import *


class UserAdmin(AuthUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = [
        ['Персональные данные', {'fields': ['email', 'first_name', 'last_name', 'phone', 'address']}],
        ['Метки и разрешения', {'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']}],
        ['Важные даты', {'fields': ['last_login', 'date_joined']}],
        ['Безопасность', {'fields': ['password']}]
    ]

    add_fieldsets = [
        [None, {'fields': ['email', 'password1', 'password2'], 'classes': ['wide']}],
    ]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    ordering = ['name']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'name', 'price', 'quantity', 'active']
    list_filter = ['category', 'active']
    search_fields = ['name', 'brand', 'vendor']
    ordering = ['vendor']


def send_mail(modeladmin, request, queryset):
    email = get_object_safe(Email, code='subscription')
    if email is None: return
    for item in queryset: email.send(item.email)
send_mail.short_description = 'Отправить письмо'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'activated']
    readonly_fields = ['activated']
    ordering = ['-activated']
    actions = [send_mail]


class OrderItemInline(admin.TabularInline):
    verbose_name = 'Элемент заказа'
    verbose_name_plural = 'Элементы заказа'
    model = Order.items.through


class OrderItemAdmin(admin.ModelAdmin):
    readonly_fields = ['price']
    get_model_perms = lambda self, req: {}


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'status', 'created', 'phone', 'delivery_type', 'total']
    readonly_fields = ['id', 'created', 'items_total', 'discount', 'delivery_price', 'total']
    exclude = ['items']
    ordering = ['-created']

    fieldsets = [
        ['Основное', {'fields': ['id', 'created', 'status', 'manager']}],
        ['Контакты и доставка', {'fields': ['phone', 'delivery_type', 'delivery_date', 'delivery_address']}],
        ['Детализация', {'fields': ['items_total', 'coupon', 'discount', 'delivery_price', 'correction', 'total']}],
    ]

    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        if request.user.is_superuser: return qs
        return qs.filter(manager=request.user)


class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'free']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['type', 'value', 'active']


admin.site.register(User, UserAdmin)
admin.site.register(Component)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Email)

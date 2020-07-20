from django.contrib import admin
from .models import Order, OrderItems
# Register your models here.

class OrderInline(admin.StackedInline):
    model = OrderItems
    autocomplete_fields = ('order',)
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_status_display', 'total_price', 'get_consume_location_display']
    search_fields = ('user__username', 'user__email', 'order__id',)

    inlines = (OrderInline, )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItems)
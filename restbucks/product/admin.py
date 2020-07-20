from django.contrib import admin
from .models import Option, Product, Customazition
# Register your models here.

class OptionInline(admin.StackedInline):
    model = Option
    autocomplete_fields = ['product']
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'price']
    search_fields = ('title', 'id', 'slug', 'price')

    inlines = (OptionInline, )

admin.site.register(Product, ProductAdmin)
admin.site.register(Option)
admin.site.register(Customazition)
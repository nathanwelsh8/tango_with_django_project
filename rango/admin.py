from django.contrib import admin

# Register your models here.
from rango.models import Category, Page


class PageAdmin(admin.ModelAdmin):
    ' this class determines what is displayed when looking up the Pages in admin section'
    list_display = ('title', 'category', 'url')


admin.site.register(Category)
admin.site.register(Page, PageAdmin)

from django.contrib import admin

# Register your models here.
from rango.models import Category, Page


class PageAdmin(admin.ModelAdmin):
    ' this class determines what is displayed when looking up the Pages in admin section'
    list_display = ('title', 'category', 'url')

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)

from django.contrib import admin

from .models import Category, CategoryAdmin, MenuItem

admin.site.register(MenuItem)
admin.site.register(Category, CategoryAdmin)

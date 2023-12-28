from django.contrib import admin
from .models import *


class SpecsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_create', 'is_published', 'moderator_nickname')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'time_create', 'moderator_nickname')
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('moderator_nickname',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.moderator_nickname = request.user
        obj.save()

    # def get_html_image(self, object):
    #     if object.image:
    #         return mark_safe(f"<img src='{object.image.url}' width=150>")
    #
    # get_html_image.short_description = "Изображение"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('id',)
    prepopulated_fields = {"slug": ("name",)}


class AddSpecAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'time', 'image')
    list_display_links = ('id', 'nickname')
    search_fields = ('nickname', 'content')
    list_filter = ('time',)
    readonly_fields = ('nickname',)


admin.site.register(Specs, SpecsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(AddSpec, AddSpecAdmin)

admin.site.site_title = 'Админ-панель DotaSpecs'
admin.site.site_header = 'Админ-панель DotaSpecs.com'

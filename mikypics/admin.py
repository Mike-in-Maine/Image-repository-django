from django.contrib import admin
from .models import Photo, Tag, Category

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'date_taken', 'uploaded_at')
    filter_horizontal = ('tags',)  # This adds a UI for selecting tags in admin

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

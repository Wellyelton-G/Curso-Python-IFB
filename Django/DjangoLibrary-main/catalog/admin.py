from django.contrib import admin
from .models import Book
from django.utils.html import format_html

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'total_copies', 'available_copies', 'cover_image_tag']
    readonly_fields = ['available_copies']
    search_fields = ['title', 'author', 'isbn']

    def cover_image_tag(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-width:100px; max-height:150px;">'.format(obj.cover_image.url))
        return "-"
    
    cover_image_tag.short_description = 'Cover'
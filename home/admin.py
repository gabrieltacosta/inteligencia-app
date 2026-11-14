from django.contrib import admin
from .models import Link

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'href', 'icon', 'alt', 'target', 'order',)
    list_editable = ('order',)
    list_display_links = ('label',)
    search_fields = ('label', 'href')
    ordering = ('-order',)
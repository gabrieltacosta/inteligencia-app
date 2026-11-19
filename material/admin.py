from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from .models import Material
from .resources import MaterialResource


@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    resource_classes = [MaterialResource]
    list_display = ('controle_aa', 'image_tag', 'nome', 'localizacao', 'patrimonio', 'recibo', 'anexo_recibo', 'data_inclusao', 'data_devolucao', 'anexo_devolucao', 'updated_at')
    list_display_links = ('nome',)
    readonly_fields = ('controle_aa',)
    search_fields = ('controle_aa', 'nome', 'patrimonio', 'recibo', 'localizacao', 'observacao')
    list_filter = ('localizacao',)
    ordering = ('controle_aa',)

    def image_tag(self, obj):
        if obj.foto:
            return format_html('<a href="{}"><img src="{}" width="50" height="50" /></a>', obj.foto.url, obj.foto.url)
        return "-"
    image_tag.short_description = 'Foto'
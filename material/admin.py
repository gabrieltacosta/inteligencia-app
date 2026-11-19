from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from weasyprint import HTML
from .models import Material
from .resources import MaterialResource


@admin.action(description="Exportar PDF")
def exportar_pdf(modeladmin, request, queryset):
    html_string = render_to_string("inventario_material_pdf.html", {"objetos": queryset})
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Inventario Material Carga AA 6º BPRv.pdf"'

    return response


@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    resource_classes = [MaterialResource]
    list_display = ('controle_aa', 'image_tag', 'nome', 'localizacao', 'patrimonio', 'recibo', 'anexo_recibo', 'data_inclusao', 'data_devolucao', 'anexo_devolucao', 'updated_at')
    list_display_links = ('nome',)
    readonly_fields = ('controle_aa',)
    search_fields = ('controle_aa', 'nome', 'patrimonio', 'recibo', 'localizacao', 'observacao')
    list_filter = ('localizacao',)
    ordering = ('controle_aa',)
    list_per_page = 10
    actions = [exportar_pdf]

    def image_tag(self, obj):
        if obj.foto:
            return format_html('<a href="{}"><img src="{}" width="50" height="50" /></a>', obj.foto.url, obj.foto.url)
        return "-"
    image_tag.short_description = 'Foto'
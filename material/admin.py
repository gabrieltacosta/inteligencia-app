from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import render
from import_export.admin import ImportExportModelAdmin
from weasyprint import HTML
from .models import Material, MovimentacaoMaterial
from .resources import MaterialResource
from core.utils import _gerar_qr_base64


@admin.action(description="Exportar PDF")
def exportar_pdf(modeladmin, request, queryset):
    html_string = render_to_string("inventario_material_pdf.html", {"objetos": queryset})
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Inventario Material Carga AA 6º BPRv.pdf"'

    return response


@admin.action(description="Gerar etiquetas / QR Code")
def gerar_etiquetas_qrcode(modeladmin, request, queryset):
  etiquetas = []
  for material in queryset:
    # Aponta para a listagem já filtrando pelo controle_aa e ativando o modo card
    url_relativa = reverse("material:qr_detalhe", kwargs={"material_id": material.id})  # ajuste o namespace/nome da sua url
    url_completa = (
        request.build_absolute_uri(url_relativa)
    )

    etiquetas.append({
        "material": material,
        "qr_base64": _gerar_qr_base64(url_completa),
        "url_destino": url_completa,
    })

  return render(
      request, "admin/material/etiquetas_pdf.html", {"etiquetas": etiquetas}
  )

class MovimentacaoMaterialInline(admin.TabularInline):
    model = MovimentacaoMaterial
    extra = 0
    readonly_fields = ("data_movimentacao",)
    fields = ("tipo", "localizacao_anterior", "localizacao_nova", "observacao", "data_movimentacao")
    can_delete = False

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
    inlines = [MovimentacaoMaterialInline]
    actions = [exportar_pdf, gerar_etiquetas_qrcode]

    def image_tag(self, obj):
        if obj.foto:
            return format_html('<a href="{}"><img src="{}" width="50" height="50" /></a>', obj.foto.url, obj.foto.url)
        return "-"
    image_tag.short_description = 'Foto'
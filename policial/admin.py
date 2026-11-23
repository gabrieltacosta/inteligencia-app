from django.contrib import admin
from django.utils.html import format_html
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from import_export.admin import ImportExportModelAdmin
from weasyprint import HTML
from .models import PostGrad, PlanoChamada, ConstaQue
from .resources import PlanoChamadaResource, ConstaQueResource


class ConstaQueInline(admin.StackedInline):
    model = ConstaQue
    can_delete = False
    extra = 0
    exclude = ('incluir_plano_chamada',)


@admin.register(PostGrad)
class PostGradAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    list_filter = ("title",)



@admin.action(description="Exportar PDF")
def exportar_pdf(modeladmin, request, queryset):
    html_string = render_to_string("plano_chamada_pdf.html",{"objetos": queryset})
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Plano de Chamada.pdf"'

    return response
@admin.register(PlanoChamada)
class PlanoChamadaAdmin(ImportExportModelAdmin):
    resource_classes = [PlanoChamadaResource]
    list_display = ('foto', 'post_grad', 're_sem_digito', 'nome_guerra', 'nome_completo', 'subunidade', 'logradouro', 'numero', 'complemento', 'bairro', "municipio", "uf", "celulares", "telefone", "recado", "updated_at")
    list_display_links = ('re_sem_digito',)
    search_fields = ('re', 'nome_guerra', 'nome_completo')
    list_filter = ('post_grad', 'subunidade', 'situacao')
    inlines = [ConstaQueInline]
    ordering = ('post_grad__id','re')
    actions = [exportar_pdf]
    list_per_page = 25

    class Media:
        js = ('js/mascara_re.js',)

    def re_sem_digito(self, obj):
        return obj.re.split("-")[0]
    re_sem_digito.short_description = "R.E. sem dígito"

    def foto(self, obj):
        if obj.imagem:
            return format_html('<a href="{}"><img src="{}" width="50" height="50" /></a>', obj.imagem.url, obj.imagem.url)
        return "-"
    foto.short_description = 'Foto'

    def get_import_data_kwargs(self, **kwargs):
        data_kwargs = super().get_import_data_kwargs(**kwargs)
        request = kwargs.get('request')
        form = kwargs.get('form')

        if request and 'import_file' in request.FILES:
            data_kwargs['file'] = request.FILES['import_file']
        elif form and hasattr(form, 'cleaned_data'):
            data_kwargs['file'] = form.cleaned_data.get('import_file')

        return data_kwargs



@admin.register(ConstaQue)
class CostaQueAdmin(ImportExportModelAdmin):
    resource_classes = [ConstaQueResource,]
    list_display = ('foto', 'conduta_colorida', 'post_grad', 're_sem_digito', 'nome_guerra', 'subunidade', "consulta_resumo", "p2_resumo", "jd_resumo", "observacao_resumo", "updated_at")
    list_display_links = ('re_sem_digito',)
    search_fields = ('re', 'nome_guerra', 'nome_completo', "consulta", "p2", "jd")
    list_filter = ('conduta', 'subunidade', 'post_grad')
    autocomplete_fields = ('policial',)
    ordering = ('post_grad',)
    list_per_page = 25

    class Media:
        js = ('js/mascara_re.js',)

    def re_sem_digito(self, obj):
        return obj.re.split("-")[0]
    re_sem_digito.short_description = "R.E. sem dígito"

    def foto(self, obj):
        if obj.imagem:
            return format_html('<a href="{}"><img src="{}" width="50" height="50" /></a>', obj.imagem.url, obj.imagem.url)
        return "-"
    foto.short_description = 'Foto'

    def get_import_data_kwargs(self, **kwargs):
        data_kwargs = super().get_import_data_kwargs(**kwargs)
        request = kwargs.get('request')
        form = kwargs.get('form')

        if request and 'import_file' in request.FILES:
            data_kwargs['file'] = request.FILES['import_file']
        elif form and hasattr(form, 'cleaned_data'):
            data_kwargs['file'] = form.cleaned_data.get('import_file')

        return data_kwargs

    def conduta_colorida(self, obj):
        estilos = {
            'SN': ('#dcfce7', '#166534'),  # Fundo verde claro, texto verde escuro
            'PN': ('#fef9c3', '#854d0e'),  # Fundo amarelo claro, texto âmbar escuro
            'CN': ('#fee2e2', '#991b1b'),  # Fundo vermelho claro, texto vermelho escuro
        }

        label = obj.get_conduta_display()

        if obj.conduta in estilos:
            bg_color, text_color = estilos[obj.conduta]
            return format_html(
                '<span style="background-color: {}; color: {}; padding: 3px 8px; '
                'border-radius: 4px; font-weight: 600; display: inline-block; '
                'white-space: nowrap;">{}</span>',
                bg_color,
                text_color,
                label,
            )

        return "-"

    conduta_colorida.short_description = 'Conduta'
    conduta_colorida.admin_order_field = 'conduta'
from django.contrib import admin
from django.utils.html import format_html
from .models import PostGrad, PlanoChamada, ConstaQue


class ConstaQueInline(admin.StackedInline):
    model = ConstaQue
    can_delete = False
    extra = 0


@admin.register(PostGrad)
class PostGradAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    list_filter = ("title",)


@admin.register(PlanoChamada)
class PlanoChamadaAdmin(admin.ModelAdmin):
    list_display = ('foto', 'post_grad', 're_sem_digito', 'nome_guerra', 'nome_completo', 'subunidade', 'logradouro', 'numero', 'complemento', 'bairro', "municipio", "uf", "celulares", "telefone", "recado", "updated_at")
    list_display_links = ('re_sem_digito',)
    search_fields = ('re', 'nome_guerra', 'nome_completo')
    list_filter = ('post_grad', 'subunidade', 'situacao')
    inlines = [ConstaQueInline]

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



@admin.register(ConstaQue)
class NadaCostaAdmin(admin.ModelAdmin):
    list_display = ('foto', 'conduta', 'post_grad', 're_sem_digito', 'nome_guerra', 'subunidade', "consulta", "p2", "jd", "observacao", "updated_at")
    list_display_links = ('re_sem_digito',)
    search_fields = ('re', 'nome_guerra', 'nome_completo', "consulta", "p2", "jd")
    list_filter = ('conduta', 'subunidade', 'post_grad')
    autocomplete_fields = ('policial',)
    ordering = ('post_grad',)

    def re_sem_digito(self, obj):
        return obj.re.split("-")[0]
    re_sem_digito.short_description = "R.E. sem dígito"

    def foto(self, obj):
        if obj.imagem:
            return format_html('<a href="{}"><img src="{}" width="50" height="50" /></a>', obj.imagem.url, obj.imagem.url)
        return "-"
    foto.short_description = 'Foto'
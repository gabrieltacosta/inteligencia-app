from django.db import models
from django.template.defaultfilters import truncatechars
from core.utils import generate_cuid, validar_re, get_policial_upload_image_path, compress_and_convert_to_webp


class PostGrad(models.Model):
    title = models.CharField(max_length=10, verbose_name="Posto/Graduação")

    class Meta:
        ordering = ["id"]
        verbose_name = "Post/Grad"
        verbose_name_plural = "Post/Grad"

    def __str__(self):
        return self.title


class PlanoChamada(models.Model):

    UF_CHOICES = (
        ("SP", "São Paulo"),
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso	"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais	"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    )

    SUBUNIDADE_CHOICES = (
        ("EM", "Estado Maior"),
        ("1CIA", "1ª Cia"),
        ("2CIA", "2ª Cia"),
        ("3CIA", "3ª Cia"),
        ("4CIA", "4ª Cia"),
        ("OUTRA", "Outra"),
    )

    SITUACA0_CHOICES = (
        ("ATIVO", "Ativo"),
        ("INATIVO", "Inativo"),
        ("LSV", "L.S.V."),
        ("LTS", "L.T.S."),
        ("AGREGADO", "Agregado"),
        ("INCAPFISICA", "Incapacidade Física")
    )

    id = models.CharField(primary_key=True, default=generate_cuid, editable=False, max_length=50)
    post_grad = models.ForeignKey(PostGrad, on_delete=models.PROTECT, verbose_name="Post/Grad")
    re =models.CharField(max_length=9, unique=True, null=False, blank=False, verbose_name="R.E.", validators=[validar_re])
    nome_guerra = models.CharField(max_length=50, verbose_name="Nome de Guerra")
    nome_completo = models.CharField(max_length=100, verbose_name="Nome Completo")
    subunidade = models.CharField(max_length=5, choices=SUBUNIDADE_CHOICES, verbose_name="Subunidade")
    situacao = models.CharField(max_length=50, choices=SITUACA0_CHOICES, blank=True, null=True, verbose_name="Situação")
    logradouro = models.CharField(max_length=100, verbose_name="Logradouro")
    numero = models.IntegerField(verbose_name="Número")
    complemento = models.CharField(max_length=50, null=True, blank=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    uf = models.CharField(max_length=2, choices=UF_CHOICES ,verbose_name="UF")
    celulares = models.CharField(max_length=50, verbose_name="Celulares")
    telefone = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telefone Residencial")
    recado = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telefones para Recado")
    imagem = models.ImageField(upload_to=get_policial_upload_image_path, null=True, blank=True, verbose_name="Foto")
    
    created_at = models.DateField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateField(auto_now=True, verbose_name="Atualizado em")

    class Meta():
        ordering = ["post_grad__id"]
        verbose_name = "Plano de Chamada"
        verbose_name_plural = "Plano de Chamada"

    def __str__(self):
        return f"{self.post_grad} {self.re} {self.nome_guerra}"

    def save(self, *args, **kwargs):
        campos_maiusculos = [
            're',
            'nome_guerra',
            'nome_completo',
            'logradouro',
            'complemento',
            'bairro',
            'municipio',
        ]

        for campo in campos_maiusculos:
            valor = getattr(self, campo, None)
            if valor and isinstance(valor, str):
                setattr(self, campo, valor.strip().upper())

        if self.imagem and not self.imagem.name.endswith('.webp'):
            compress_and_convert_to_webp(self.imagem, max_width=400, quality=85, is_avatar=False)

        super().save(*args, **kwargs)




class ConstaQue(models.Model):
    SUBUNIDADE_CHOICES = (
        ("EM", "Estado Maior"),
        ("1CIA", "1ª Cia"),
        ("2CIA", "2ª Cia"),
        ("3CIA", "3ª Cia"),
        ("4CIA", "4ª Cia"),
        ("OUTRA", "Outra"),
    )

    CONDUTA_CHOICES = (
        ("SN", "Sem Novidade"),
        ("CN", "Com Novidade"),
        ("PN", "Possível Novidade"),
    )

    id = models.CharField(primary_key=True, default=generate_cuid, editable=False, max_length=50)
    policial = models.OneToOneField(
        PlanoChamada,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consta_que",
        verbose_name="Policial (Plano de Chamada)"
    )

    post_grad = models.ForeignKey(PostGrad, on_delete=models.PROTECT, verbose_name="Post/Grad")
    re = models.CharField(max_length=9, unique=True, validators=[validar_re], verbose_name="R.E.")
    nome_guerra = models.CharField(max_length=50, verbose_name="Nome de Guerra")
    nome_completo = models.CharField(max_length=100, verbose_name="Nome Completo")
    subunidade = models.CharField(max_length=5, choices=SUBUNIDADE_CHOICES, blank=True, null=True, verbose_name="Subunidade")
    imagem = models.ImageField(upload_to=get_policial_upload_image_path, null=True, blank=True, verbose_name="Foto")


    conduta = models.CharField(max_length=2, choices=CONDUTA_CHOICES, default= "SN", blank=True, null=True, verbose_name="Conduta")
    consulta = models.TextField(blank=True, null=True, verbose_name="Consulta")
    p2 = models.TextField(blank=True, null=True, verbose_name="P2")
    jd = models.TextField(blank=True, null=True, verbose_name="JD")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observações")

    created_at = models.DateField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateField(auto_now=True, verbose_name="Atualizado em")

    @property
    def ativo_na_unidade(self):
        return self.policial is not None

    @property
    def consulta_resumo(self):
        return truncatechars(self.consulta, 30)

    @property
    def p2_resumo(self):
        return truncatechars(self.p2, 30)

    @property
    def jd_resumo(self):
        return truncatechars(self.jd, 30)

    @property
    def observacao_resumo(self):
        return truncatechars(self.observacao, 30)

    class Meta:
        ordering = ["post_grad__id"]
        verbose_name = "Consta Que"
        verbose_name_plural = "Consta Que"

    # def __str__(self):
    #     return f"{self.policial.post_grad} {self.policial.re} {self.policial.nome_guerra}"

    def save(self, *args, **kwargs):
        campos_maiusculos = [
            're',
            'nome_guerra',
            'nome_completo',
            # Adicione 'consulta', 'p2', 'jd', 'observacao' aqui se também quiser esses em caixa alta
        ]

        for campo in campos_maiusculos:
            valor = getattr(self, campo, None)
            if valor and isinstance(valor, str):
                setattr(self, campo, valor.strip().upper())

        if self.imagem and not self.imagem.name.endswith('.webp'):
            compress_and_convert_to_webp(self.imagem, max_width=400, quality=85, is_avatar=False)

        super().save(*args, **kwargs)
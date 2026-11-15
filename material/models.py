from django.db import models, transaction
from django.db.models import Max
from core.utils import get_materials_upload_recibos_path, get_materials_upload_images_path, compress_and_convert_to_webp, generate_cuid, validar_arquivo_pdf


class Material(models.Model):

    LOCALIZACAO_CHOICES = [
        ('AA-BATALHAO', 'AA - Batalhão'),
        ('SAI-1CIA', 'SAI - 1ª Cia'),
        ('SAI-2CIA', 'SAI - 2ª Cia'),
        ('SAI-3CIA', 'SAI - 3ª Cia'),
        ('SAI-4CIA', 'SAI - 4ª Cia'),
        ]

    id = models.CharField(primary_key=True, default=generate_cuid, editable=False, max_length=50)
    controle_aa = models.CharField(max_length=20, unique=True, editable=False, blank=True, verbose_name="Controle AA", help_text="Código de controle AA (ex: AA-0001)")
    nome = models.CharField(max_length=100, help_text="Nome do material", verbose_name="Material")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição detalhada do material (opcional)", verbose_name="Descrição")
    patrimonio = models.CharField(max_length=50, blank=True, null=True, help_text="Número de patrimônio do material (opcional)", default="Sem Patrimônio", verbose_name="Patrimônio")
    localizacao = models.CharField(max_length=100, blank=True, null=True, choices=LOCALIZACAO_CHOICES, help_text="Localização do material (opcional)", verbose_name="Localização")
    recibo = models.CharField(max_length=50, help_text="Número do recibo do material (opcional)", blank=True, null=True, default="Sem Recibo")
    anexo_recibo = models.FileField(upload_to=get_materials_upload_recibos_path, blank=True, null=True, validators=[validar_arquivo_pdf], help_text="Anexo do recibo do material em PDF (opcional)", verbose_name="Anexo Recibo Entrada")
    data_inclusao = models.DateField(help_text="Data de inclusão do material (opcional)", blank=True, null=True)
    observacao = models.TextField(blank=True, null=True, help_text="Observações adicionais sobre o material (opcional)", verbose_name="Observações")
    foto = models.ImageField(upload_to=get_materials_upload_images_path, blank=True, null=True, help_text="Foto do material (opcional)", verbose_name="Foto")
    data_devolucao = models.DateField(blank=True, null=True, help_text="Data de devolução do material (opcional)", verbose_name="Data de Devolução")
    anexo_devolucao = models.FileField(upload_to=get_materials_upload_recibos_path, blank=True, null=True, validators=[validar_arquivo_pdf], help_text="Anexo do recibo de devolução do material em PDF (opcional)", verbose_name="Anexo Recibo Saída")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")


    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiais"
        ordering = ['controle_aa']


    def __str__(self):
        return f"{self.nome} - {self.patrimonio if self.patrimonio else 'Sem Patrimônio'}"


    @classmethod
    def _gerar_proximo_controle_aa(cls):
        ultimo_codigo = cls.objects.aggregate(Max('controle_aa'))['controle_aa__max']

        if ultimo_codigo:
            numero_atual = int(ultimo_codigo.split('-')[1])
            proximo_numero = numero_atual + 1
        else:
            proximo_numero = 1

        return f'AA-{proximo_numero:04d}'


    def save(self, *args, **kwargs):
        # Chama a função para comprimir e converter a imagem para WebP antes de salvar
        if self.foto and not self.foto.name.endswith('.webp'):
            compress_and_convert_to_webp(self.foto, max_width=1200, quality=80, is_avatar=False)

        if not self.controle_aa:
            with transaction.atomic():
                Material.objects.select_for_update().all()
                self.controle_aa = self._gerar_proximo_controle_aa()
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

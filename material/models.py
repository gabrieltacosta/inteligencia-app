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
        localizacao_antiga = None
        devolucao_antiga = None
        if self.pk:
            original = Material.objects.filter(pk=self.pk).first()
            if original:
                localizacao_antiga = original.localizacao
                devolucao_antiga = original.data_devolucao
        # Chama a função para comprimir e converter a imagem para WebP antes de salvar
        if self.foto and not self.foto.name.endswith('.webp'):
            compress_and_convert_to_webp(self.foto, max_width=1200, quality=80, is_avatar=False)

        with transaction.atomic():
            if not self.controle_aa:
                Material.objects.select_for_update().all()
                self.controle_aa = self._gerar_proximo_controle_aa()

            super().save(*args, **kwargs)

            if not self.pk or localizacao_antiga is None and not devolucao_antiga:
                pass

            if localizacao_antiga != self.localizacao and (self.pk is not None):
                MovimentacaoMaterial.objects.create(
                    material=self,
                    tipo='TRANSFERENCIA',
                    localizacao_anterior=localizacao_antiga,
                    localizacao_nova=self.localizacao,
                    observacao="Atualização automática de localização no cadastro.",
                )

            if devolucao_antiga != self.data_devolucao and self.data_devolucao:
                MovimentacaoMaterial.objects.create(
                    material=self,
                    tipo='DEVOLUCAO',
                    localizacao_anterior=self.localizacao,
                    localizacao_nova=self.localizacao,
                    observacao=f"Data de devolução registrada: {self.data_devolucao}",
                )



class MovimentacaoMaterial(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada / Inclusão'),
        ('TRANSFERENCIA', 'Transferência de Localização'),
        ('DEVOLUCAO', 'Devolução'),
        ('AJUSTE', 'Ajuste / Observação'),
    ]

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="movimentacoes",
        verbose_name="Material",
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='TRANSFERENCIA',
        verbose_name="Tipo de Movimentação",
        help_text="Escolha o tipo de movimentação."
    )
    localizacao_anterior = models.CharField(
        max_length=100,
        choices=Material.LOCALIZACAO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Localização Anterior",
    )
    localizacao_nova = models.CharField(
        max_length=100,
        choices=Material.LOCALIZACAO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Localização Nova",
    )
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    data_movimentacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Movimentação")

    class Meta:
        verbose_name = "Movimentação do Material"
        verbose_name_plural = "Histórico de Movimentações"
        ordering = ['-data_movimentacao']

    def _str_(self):
        return f"{self.material.controle_aa} - {self.get_tipo_display()}"
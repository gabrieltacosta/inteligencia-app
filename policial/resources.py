import re
import hashlib
import unicodedata
import openpyxl
from openpyxl.cell.rich_text import CellRichText, TextBlock
from django.core.cache import cache
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import PlanoChamada, PostGrad, ConstaQue


def _normalizar_texto(texto):
    """Remove acentos, espaços extras e deixa em maiúsculo para comparação."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', sem_acento).strip().upper()


class PlanoChamadaResource(resources.ModelResource):
    post_grad = fields.Field(
        column_name="POSTO/GRAD",
        attribute="post_grad",
        widget=ForeignKeyWidget(PostGrad, field='title')
    )
    re = fields.Field(column_name='RE', attribute='re')
    nome_completo = fields.Field(column_name='NOME', attribute='nome_completo')
    subunidade = fields.Field(column_name='SUBUNIDADE', attribute='subunidade')
    situacao = fields.Field(column_name='SITUAÇÃO', attribute='situacao')
    logradouro = fields.Field(column_name='ENDEREÇO RESIDENCIAL', attribute='logradouro')
    numero = fields.Field(column_name='NÚMERO', attribute='numero')
    complemento = fields.Field(column_name='COMPLEMENTO', attribute='complemento')
    bairro = fields.Field(column_name='BAIRRO', attribute='bairro')
    municipio = fields.Field(column_name='MUNICÍPIO', attribute='municipio')
    uf = fields.Field(column_name='UF', attribute='uf')
    telefone = fields.Field(column_name='TELEFONE RESIDENCIAL', attribute='telefone')
    celulares = fields.Field(column_name='TELEFONE (S)', attribute='celulares')
    recado = fields.Field(column_name='TELEFONE RECADO', attribute='recado')

    MAPA_SUBUNIDADE = {
        "EM": "EM",
        "ESTADO MAIOR": "EM",
        "1A CIA": "1CIA",
        "1 CIA": "1CIA",
        "1CIA": "1CIA",
        "2A CIA": "2CIA",
        "2 CIA": "2CIA",
        "2CIA": "2CIA",
        "3A CIA": "3CIA",
        "3 CIA": "3CIA",
        "3CIA": "3CIA",
        "4A CIA": "4CIA",
        "4 CIA": "4CIA",
        "4CIA": "4CIA",
        "OUTRA": "OUTRA",
    }

    MAPA_SITUACAO = {
        "ATIVO": "ATIVO",
        "INATIVO": "INATIVO",
        "LSV": "LSV",
        "L.S.V.": "LSV",
        "LTS": "LTS",
        "L.T.S.": "LTS",
        "AGREGADO": "AGREGADO",
        "INCAPFISICA": "INCAPFISICA",
        "INCAPACIDADE FISICA": "INCAPFISICA",
    }

    class Meta:
        model = PlanoChamada
        import_id_fields = ('re',)
        skip_unchanged = True
        report_skipped = True
        fields = (
            'post_grad', 're', 'nome_completo', 'nome_guerra', 'subunidade', 'situacao',
            'logradouro', 'numero', 'complemento', 'bairro', 'municipio',
            'uf', 'celulares', 'telefone', 'recado'
        )

    def before_import(self, dataset, **kwargs):
        self.nomes_guerra_negrito = {}
        arquivo = kwargs.get('file') or kwargs.get('import_file')

        # Gera uma assinatura única baseada nos dados do dataset para ligar o preview à confirmação
        assinatura_dados = "|".join(str(row) for row in dataset[:50])
        cache_key = f"import_negrito_{self.__class__.__name__}_{hashlib.md5(assinatura_dados.encode('utf-8')).hexdigest()}"

        if arquivo:
            try:
                arquivo.seek(0)
                wb = openpyxl.load_workbook(arquivo, rich_text=True, data_only=True)
                ws = wb.active

                col_nome_idx = None
                for idx, cell in enumerate(ws[1], start=1):
                    if str(cell.value or '').strip().upper() == 'NOME':
                        col_nome_idx = idx
                        break

                if col_nome_idx:
                    for row_idx in range(2, ws.max_row + 1):
                        val = ws.cell(row=row_idx, column=col_nome_idx).value
                        partes_negrito = []

                        if isinstance(val, CellRichText):
                            for bloco in val:
                                if isinstance(bloco, TextBlock) and bloco.font:
                                    is_bold = bool(getattr(bloco.font, 'b', False) or getattr(bloco.font, 'bold', False))
                                    if is_bold:
                                        texto = bloco.text.strip()
                                        if texto:
                                            partes_negrito.append(texto)

                        if partes_negrito:
                            chave = _normalizar_texto(str(val))
                            self.nomes_guerra_negrito[chave] = " ".join(partes_negrito)

                arquivo.seek(0)

                # Salva o mapeamento extraído por 30 minutos para a etapa de confirmação
                if self.nomes_guerra_negrito:
                    cache.set(cache_key, self.nomes_guerra_negrito, timeout=1800)
            except Exception:
                pass
        else:
            # Na etapa de confirmação (sem request.FILES), recupera o mapeamento salvo no preview
            cached_map = cache.get(cache_key)
            if cached_map:
                self.nomes_guerra_negrito = cached_map

    def skip_row(self, instance, original, row, import_validation_errors=None):
        re_val = str(row.get('RE') or '').strip()
        nome_val = str(row.get('NOME') or '').strip()
        if not re_val or not nome_val:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def before_import_row(self, row, **kwargs):
        # 1. Posto/Graduação
        pg_val = str(row.get('POSTO/GRAD') or '').strip()
        if pg_val:
            PostGrad.objects.get_or_create(title=pg_val)
        row['POSTO/GRAD'] = pg_val

        # 2. Formata R.E. (000.000-0)
        raw_re = re.sub(r'[^0-9A-Za-z]', '', str(row.get('RE') or '')).upper()
        if len(raw_re) == 7:
            row['RE'] = f"{raw_re[:3]}.{raw_re[3:6]}-{raw_re[6]}"
        else:
            row['RE'] = str(row.get('RE') or '').strip().upper()

        # 3. Extrai Nome de Guerra pelo negrito (ou último sobrenome)
        nome = str(row.get('NOME') or '').strip()
        nome_guerra_negrito = getattr(self, 'nomes_guerra_negrito', {}).get(_normalizar_texto(nome))

        if nome_guerra_negrito:
            row['nome_guerra'] = nome_guerra_negrito[:50]
        else:
            partes = nome.split()
            row['nome_guerra'] = (partes[-1] if len(partes) > 1 else nome)[:50]

        # 4. Converte Subunidade ("2ª Cia" -> "2CIA")
        sub_norm = _normalizar_texto(row.get('SUBUNIDADE'))
        row['SUBUNIDADE'] = self.MAPA_SUBUNIDADE.get(sub_norm, 'OUTRA')

        # 5. Converte Situação ("Ativo" -> "ATIVO")
        sit_norm = _normalizar_texto(row.get('SITUAÇÃO'))
        row['SITUAÇÃO'] = self.MAPA_SITUACAO.get(sit_norm, 'ATIVO')

        # 6. Converte NÚMERO para inteiro
        num_str = re.sub(r'\D', '', str(row.get('NÚMERO') or ''))
        row['NÚMERO'] = int(num_str) if num_str else 0

        # 7. Padroniza UF e campos obrigatórios
        uf = str(row.get('UF') or 'SP').strip().upper()[:2]
        row['UF'] = uf if uf else 'SP'
        row['ENDEREÇO RESIDENCIAL'] = str(row.get('ENDEREÇO RESIDENCIAL') or 'Não informado').strip()
        row['BAIRRO'] = str(row.get('BAIRRO') or 'Não informado').strip()
        row['MUNICÍPIO'] = str(row.get('MUNICÍPIO') or 'Não informado').strip()
        row['TELEFONE (S)'] = str(row.get('TELEFONE (S)') or 'Não informado').strip()

        # 8. Junta TELEFONE RECADO e TELEFONE RECADO II
        rec1 = str(row.get('TELEFONE RECADO') or '').strip()
        rec2 = str(row.get('TELEFONE RECADO II') or '').strip()
        recados = [r for r in (rec1, rec2) if r and r.lower() != 'none']
        row['TELEFONE RECADO'] = ' / '.join(recados)[:100] if recados else ''


class ConstaQueResource(resources.ModelResource):
    post_grad = fields.Field(
        column_name="Grad",
        attribute="post_grad",
        widget=ForeignKeyWidget(PostGrad, field='title')
    )
    re = fields.Field(column_name='RE', attribute='re')
    nome_completo = fields.Field(column_name='NOME', attribute='nome_completo')
    subunidade = fields.Field(column_name='CIA/EM', attribute='subunidade')
    situacao = fields.Field(column_name='ATIVO/INATIVO', attribute='situacao')
    observacao = fields.Field(column_name='OBSERVAÇÕES', attribute='observacao')
    conduta = fields.Field(column_name="CONDUTA", attribute="conduta")
    consulta = fields.Field(column_name='CONSULTA', attribute='consulta')
    p2 = fields.Field(column_name='P/2', attribute='p2')
    jd = fields.Field(column_name='JD', attribute='jd')

    MAPA_SUBUNIDADE = {
        "EM": "EM",
        "ESTADO MAIOR": "EM",
        "1A CIA": "1CIA",
        "1 CIA": "1CIA",
        "1CIA": "1CIA",
        "2A CIA": "2CIA",
        "2 CIA": "2CIA",
        "2CIA": "2CIA",
        "3A CIA": "3CIA",
        "3 CIA": "3CIA",
        "3CIA": "3CIA",
        "4A CIA": "4CIA",
        "4 CIA": "4CIA",
        "4CIA": "4CIA",
        "OUTRA": "OUTRA",
    }

    MAPA_SITUACAO = {
        "ATIVO": "ATIVO",
        "INATIVO": "INATIVO",
        "LSV": "LSV",
        "L.S.V.": "LSV",
        "LTS": "LTS",
        "L.T.S.": "LTS",
        "AGREGADO": "AGREGADO",
        "INCAPFISICA": "INCAPFISICA",
        "INCAPACIDADE FISICA": "INCAPFISICA",
    }

    class Meta:
        model = ConstaQue
        import_id_fields = ('re',)  # Atualiza pelo R.E. se já existir, ou cria novo
        skip_unchanged = True
        report_skipped = True
        fields = (
            'conduta', 'policial', 'post_grad', 're', 'nome_guerra', 'nome_completo',
            'subunidade', 'situacao', 'consulta', 'p2', 'jd', 'observacao'
        )

    def before_import(self, dataset, **kwargs):
        self.nomes_guerra_negrito = {}
        arquivo = kwargs.get('file') or kwargs.get('import_file')

        # Gera uma assinatura única baseada nos dados do dataset para ligar o preview à confirmação
        assinatura_dados = "|".join(str(row) for row in dataset[:50])
        cache_key = f"import_negrito_{self.__class__.__name__}_{hashlib.md5(assinatura_dados.encode('utf-8')).hexdigest()}"

        if arquivo:
            try:
                arquivo.seek(0)
                wb = openpyxl.load_workbook(arquivo, rich_text=True, data_only=True)
                ws = wb.active

                col_nome_idx = None
                for idx, cell in enumerate(ws[1], start=1):
                    if str(cell.value or '').strip().upper() == 'NOME':
                        col_nome_idx = idx
                        break

                if col_nome_idx:
                    for row_idx in range(2, ws.max_row + 1):
                        val = ws.cell(row=row_idx, column=col_nome_idx).value
                        partes_negrito = []

                        if isinstance(val, CellRichText):
                            for bloco in val:
                                if isinstance(bloco, TextBlock) and bloco.font:
                                    is_bold = bool(getattr(bloco.font, 'b', False) or getattr(bloco.font, 'bold', False))
                                    if is_bold:
                                        texto = bloco.text.strip()
                                        if texto:
                                            partes_negrito.append(texto)

                        if partes_negrito:
                            chave = _normalizar_texto(str(val))
                            self.nomes_guerra_negrito[chave] = " ".join(partes_negrito)

                arquivo.seek(0)

                # Salva o mapeamento extraído por 30 minutos para a etapa de confirmação
                if self.nomes_guerra_negrito:
                    cache.set(cache_key, self.nomes_guerra_negrito, timeout=1800)
            except Exception:
                pass
        else:
            # Na etapa de confirmação (sem request.FILES), recupera o mapeamento salvo no preview
            cached_map = cache.get(cache_key)
            if cached_map:
                self.nomes_guerra_negrito = cached_map

    def skip_row(self, instance, original, row, import_validation_errors=None):
        re_val = str(row.get('RE') or '').strip()
        nome_val = str(row.get('NOME') or '').strip()
        if not re_val or not nome_val:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def before_import_row(self, row, **kwargs):
        # 1. Garante Posto/Graduação
        pg_val = str(row.get('Grad') or '').strip()
        if pg_val:
            PostGrad.objects.get_or_create(title=pg_val)
        row['Grad'] = pg_val

        # 2. Formata R.E. (000.000-0)
        raw_re = re.sub(r'[^0-9A-Za-z]', '', str(row.get('RE') or '')).upper()
        if len(raw_re) == 7:
            re_formatado = f"{raw_re[:3]}.{raw_re[3:6]}-{raw_re[6]}"
        else:
            re_formatado = str(row.get('RE') or '').strip().upper()
        row['RE'] = re_formatado

        # 3. Tenta vincular ao registro existente no PlanoChamada pelo R.E.
        policial_existente = PlanoChamada.objects.filter(re=re_formatado).first()
        row['policial'] = policial_existente.id if policial_existente else None

        # 4. Define Nome de Guerra (prioriza PlanoChamada > Negrito > Último sobrenome)
        nome = str(row.get('NOME') or '').strip()
        if policial_existente and policial_existente.nome_guerra:
            row['nome_guerra'] = policial_existente.nome_guerra
        else:
            nome_guerra_negrito = getattr(self, 'nomes_guerra_negrito', {}).get(_normalizar_texto(nome))
            if nome_guerra_negrito:
                row['nome_guerra'] = nome_guerra_negrito[:50]
            else:
                partes = nome.split()
                row['nome_guerra'] = (partes[-1] if len(partes) > 1 else nome)[:50]

        # 5. Converte Subunidade (CIA/EM) e Situação (ATIVO/INATIVO)
        sub_norm = _normalizar_texto(row.get('CIA/EM'))
        row['CIA/EM'] = self.MAPA_SUBUNIDADE.get(sub_norm, 'OUTRA')

        sit_norm = _normalizar_texto(row.get('ATIVO/INATIVO'))
        row['ATIVO/INATIVO'] = self.MAPA_SITUACAO.get(sit_norm, 'ATIVO')

        # 6. Limpa campos de texto do Consta Que (evita 'None' literal)
        for col in ('OBSERVAÇÕES', 'CONSULTA', 'P/2', 'JD'):
            val = str(row.get(col) or '').strip()
            row[col] = '' if val.lower() == 'none' else val
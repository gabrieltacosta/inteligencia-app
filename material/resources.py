from import_export import resources, fields
from import_export.widgets import DateWidget
from .models import Material



class MaterialResource(resources.ModelResource):
    # Mapeia os nomes exatos das colunas do Excel para os campos do Model
    nome = fields.Field(
        column_name='Material',
        attribute='nome'
    )
    patrimonio = fields.Field(
        column_name='Patrimônio',
        attribute='patrimonio'
    )
    recibo = fields.Field(
        column_name='Recibo',
        attribute='recibo'
    )
    data_inclusao = fields.Field(
        column_name='Data',
        attribute='data_inclusao',
        widget=DateWidget(format='%d/%m/%Y')
    )
    observacao = fields.Field(
        column_name='Observação',
        attribute='observacao'
    )

    class Meta:
        model = Material
        fields = ('nome', 'patrimonio', 'recibo', 'data_inclusao', 'observacao')
        import_id_fields = ()
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """
        Garante os valores padrão caso Patrimônio ou Recibo venham vazios no Excel,
        e limpa espaços extras nas strings.
        """
        for col in ['Material', 'Patrimônio', 'Recibo', 'Observação']:
            if row.get(col) is not None:
                row[col] = str(row[col]).strip()

        if not row.get('Patrimônio'):
            row['Patrimônio'] = 'Sem Patrimônio'

        if not row.get('Recibo'):
            row['Recibo'] = 'Sem Recibo'
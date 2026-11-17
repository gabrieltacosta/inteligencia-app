import os
from io import BytesIO
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
import cuid2
from PIL import Image, ImageOps



def generate_cuid():
    return cuid2.cuid_wrapper()()

# --- FUNÇÃO PARA COMPRIMIR E CONVERTER PARA WEBP ---
def compress_and_convert_to_webp(image_field, max_width=1024, quality=80, is_avatar=False):

    if not image_field or not image_field.file:
        return

    # Abre a imagem original usando o Pillow
    img = Image.open(image_field)

    img = ImageOps.exif_transpose(img)

    # Converte para RGB (necessário se a imagem original for PNG com transparência ou RGBA)
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        # Cria um fundo branco para manter a visibilidade caso haja transparência
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.convert('RGBA').split()[3])
        img = background
    else:
        img = img.convert('RGB')

    if is_avatar:
        img = ImageOps.fit(img, (max_width, max_width), Image.Resampling.LANCZOS)
    else:
    # Redimensiona proporcionalmente se a largura for maior que o permitido (ex: 1024px)
        if img.width > max_width:
            output_size = (max_width, int((max_width / img.width) * img.height))
            img = img.resize(output_size, Image.Resampling.LANCZOS)

    # Cria o buffer na memória (BytesIO)
    image_io = BytesIO()

    # Salva a imagem no buffer formato WEBP com a qualidade desejada (0-100)
    img.save(image_io, format='WEBP', quality=quality, optimize=True)

    # Altera a extensão do nome do arquivo original para .webp
    current_filename = os.path.splitext(image_field.name)[0]
    new_filename = f"{current_filename}.webp"

    # Atribuímos o novo ContentFile diretamente ao arquivo do campo, evitando disparar o save() do Django.
    image_field.file = ContentFile(image_io.getvalue())
    image_field.name = new_filename


# --- CONFIGURAÇÃO DOS CAMINHOS ---
# def get_image_upload_path(instance, filename):
#     return os.path.join('users', instance.id, filename)


# def get_cover_upload_path(instance, filename):
#     return os.path.join('post', instance.id, filename)


def get_materials_upload_recibos_path(instance, filename):
    return os.path.join('materials', str(instance.controle_aa), 'recibos', filename)

def get_materials_upload_images_path(instance, filename):
    return os.path.join('materials', str(instance.controle_aa), 'images', filename)

# Mantida para compatibilidade com as migrações antigas (0006, etc.)
def get_materials_upload_path(instance, filename):
    return get_materials_upload_images_path(instance, filename)


def get_policial_upload_image_path(instance, filename):
    return os.path.join('policial', str(instance.re), 'foto', filename)


def validar_arquivo_pdf(arquivo):
    # 1. Verifica a extensão
    if not arquivo.name.lower().endswith('.pdf'):
        raise ValidationError('Apenas arquivos no formato PDF são permitidos.')

    # 2. Verifica os primeiros 5 bytes do arquivo (assinatura padrão de todo PDF)
    cabecalho = arquivo.read(5)
    arquivo.seek(0)  # Volta o ponteiro para o início para não corromper o salvamento!

    if cabecalho != b'%PDF-':
        raise ValidationError('O arquivo enviado não é um documento PDF válido.')

    # 3. (Opcional) Limita o tamanho máximo a 5 MB
    limite_mb = 5
    if arquivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f'O arquivo PDF não pode ultrapassar {limite_mb} MB.')



validar_re = RegexValidator(regex=r'^\d{3}\.\d{3}-[0-9A-Za-z]$', message='O R.E. deve estar no formato 000.000-0 (ex: 123.456-A).')
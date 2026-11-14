import os
import shutil
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Material


MATERIAL_FILE_FIELDS = ['foto', 'anexo_recibo', 'anexo_devolucao']


def _delete_file_and_empty_dir(file_field):
    """
    Remove o arquivo do sistema de arquivos e apaga a pasta pai caso fique vazia.
    """
    if not file_field or not file_field.name:
        return

    file_path = file_field.path

    if os.path.isfile(file_path):
        os.remove(file_path)

    parent_dir = os.path.dirname(file_path)
    if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
        shutil.rmtree(parent_dir)


@receiver(post_delete, sender=Material)
def delete_material_files(sender, instance, **kwargs):
    """
    Deleta todos os arquivos (foto, anexo_recibo e anexo_devolucao) quando o Material é excluído.
    """
    for field_name in MATERIAL_FILE_FIELDS:
        file_field = getattr(instance, field_name)
        _delete_file_and_empty_dir(file_field)



@receiver(pre_save, sender=Material)
def delete_old_material_files(sender, instance, **kwargs):
    """
    Deleta arquivos antigos (foto, anexo_recibo ou anexo_devolucao) quando são substituídos ou removidos.
    """
    if not instance.pk:
        return

    try:
        old_instance = Material.objects.get(pk=instance.pk)
    except Material.DoesNotExist:
        return

    for field_name in MATERIAL_FILE_FIELDS:
        old_file = getattr(old_instance, field_name)
        new_file = getattr(instance, field_name)

        if old_file and old_file.name != getattr(new_file, 'name', None):
            _delete_file_and_empty_dir(old_file)


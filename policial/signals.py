import os
import shutil
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import PlanoChamada, ConstaQue


@receiver(post_save, sender=PlanoChamada)
def sincronizar_consta_que(sender, instance, created, **kwargs):
    # Evita loop caso o salvamento tenha sido disparado pelo ConstaQue
    if getattr(instance, '_sincronizando', False):
        return

    defaults = {
        "policial": instance,
        "post_grad": instance.post_grad,
        "re": instance.re,
        "nome_guerra": instance.nome_guerra,
        "nome_completo": instance.nome_completo,
        "subunidade": instance.subunidade,
        "imagem": instance.imagem,
        "incluir_plano_chamada": True,
    }

    consta_existente = (
        ConstaQue.objects.filter(policial=instance).first()
        or ConstaQue.objects.filter(re=instance.re).first()
    )

    if consta_existente:
        consta_existente._sincronizando = True
        for campo, valor in defaults.items():
            setattr(consta_existente, campo, valor)
        consta_existente.save()
    else:
        novo_consta = ConstaQue(**defaults)
        novo_consta._sincronizando = True
        novo_consta.save()


@receiver(post_save, sender=ConstaQue)
def sincronizar_plano_chamada(sender, instance, created, **kwargs):
    # Evita loop caso o salvamento tenha sido disparado pelo PlanoChamada
    if getattr(instance, '_sincronizando', False):
        return

    # Só cria/sincroniza no PlanoChamada se o checkbox estiver marcado
    if not instance.incluir_plano_chamada:
        return

    plano_existente = (
        instance.policial
        or PlanoChamada.objects.filter(re=instance.re).first()
    )

    if plano_existente:
        plano_existente._sincronizando = True
        plano_existente.post_grad = instance.post_grad
        plano_existente.re = instance.re
        plano_existente.nome_guerra = instance.nome_guerra
        plano_existente.nome_completo = instance.nome_completo
        plano_existente.subunidade = instance.subunidade
        if instance.imagem:
            plano_existente.imagem = instance.imagem
        plano_existente.save()
    else:
        plano_existente = PlanoChamada(
            post_grad=instance.post_grad,
            re=instance.re,
            nome_guerra=instance.nome_guerra,
            nome_completo=instance.nome_completo,
            subunidade=instance.subunidade or "OUTRA",
            situacao="ATIVO",
            logradouro="NÃO INFORMADO",
            numero=0,
            bairro="NÃO INFORMADO",
            municipio="NÃO INFORMADO",
            uf="SP",
            celulares="NÃO INFORMADO",
            imagem=instance.imagem,
        )
        plano_existente._sincronizando = True
        plano_existente.save()

    # Garante o vínculo OneToOne sem disparar novamente os signals
    if instance.policial_id != plano_existente.id:
        ConstaQue.objects.filter(pk=instance.pk).update(policial=plano_existente)


def _remover_arquivo_fisico(file_field):
    """
    Apaga o arquivo físico do disco e remove a pasta pai se ficar vazia.
    """
    if not file_field or not file_field.name:
        return

    file_path = file_field.path

    if os.path.isfile(file_path):
        os.remove(file_path)

    parent_dir = os.path.dirname(file_path)
    if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
        shutil.rmtree(parent_dir)


# --- LIMPEZA DE IMAGENS: PLANO DE CHAMADA ---

@receiver(post_delete, sender=PlanoChamada)
def delete_plano_chamada_files(sender, instance, **kwargs):
    if not instance.imagem or not instance.imagem.name:
        return

    # Só apaga se o ConstaQue não estiver usando essa mesma foto
    if not ConstaQue.objects.filter(imagem=instance.imagem.name).exists():
        _remover_arquivo_fisico(instance.imagem)


@receiver(pre_save, sender=PlanoChamada)
def delete_old_plano_chamada_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = PlanoChamada.objects.get(pk=instance.pk)
    except PlanoChamada.DoesNotExist:
        return

    old_file = old_instance.imagem
    new_file = instance.imagem

    if old_file and old_file.name != getattr(new_file, 'name', None):
        # Garante que não apague se o ConstaQue ainda apontar para a foto antiga
        if not ConstaQue.objects.filter(imagem=old_file.name).exists():
            _remover_arquivo_fisico(old_file)


# --- LIMPEZA DE IMAGENS: CONSTA QUE ---

@receiver(post_delete, sender=ConstaQue)
def delete_consta_que_files(sender, instance, **kwargs):
    if not instance.imagem or not instance.imagem.name:
        return

    # Só apaga se o PlanoChamada não estiver usando essa mesma foto
    if not PlanoChamada.objects.filter(imagem=instance.imagem.name).exists():
        _remover_arquivo_fisico(instance.imagem)


@receiver(pre_save, sender=ConstaQue)
def delete_old_consta_que_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = ConstaQue.objects.get(pk=instance.pk)
    except ConstaQue.DoesNotExist:
        return

    old_file = old_instance.imagem
    new_file = instance.imagem

    if old_file and old_file.name != getattr(new_file, 'name', None):
        # Garante que não apague se o PlanoChamada ainda apontar para a foto antiga
        if not PlanoChamada.objects.filter(imagem=old_file.name).exists():
            _remover_arquivo_fisico(old_file)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from.models import PlanoChamada, ConstaQue, PostGrad


@login_required
@permission_required('policial.view_planochamada', raise_exception=True)
def plano_chamada_list(request):

    query = request.GET.get('q', '').strip()
    subunidade_filtro = request.GET.get('subunidade', '').strip()
    post_grad_filtro = request.GET.get('post_grad', '').strip()

    policiais_qs = PlanoChamada.objects.select_related('post_grad').all()

    if subunidade_filtro:
        policiais_qs = policiais_qs.filter(subunidade=subunidade_filtro)

    if post_grad_filtro:
        policiais_qs = policiais_qs.filter(post_grad_id=post_grad_filtro)

    if query:
        subunidades_encontradas = [
            chave for chave, label in ConstaQue.SUBUNIDADE_CHOICES
            if query.lower() in label.lower()
        ]
        
        policiais_qs = policiais_qs.filter(
            Q(re__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(nome_completo__icontains=query) |
            Q(post_grad__title__icontains=query) |
            Q(subunidade__icontains=query) |
            Q(subunidade__in=subunidades_encontradas) |
            Q(municipio__icontains=query) |
            Q(bairro__icontains=query) |
            Q(celulares__icontains=query)
        )

    paginator = Paginator(policiais_qs, 25)

    page_number = request.GET.get('page')
    policiais = paginator.get_page(page_number)

    context = {
        'policiais': policiais,
        'query': query,
        'subunidade_filtro': subunidade_filtro,
        'post_grad_filtro': post_grad_filtro,
        'subunidade_choices': PlanoChamada.SUBUNIDADE_CHOICES,
        'post_grad_choices': PostGrad.objects.all(),
    }

    return render(request, 'policiais.html', context)


@login_required
@permission_required('policial.view_constaque', raise_exception=True)
def consta_que_list(request):
    query = request.GET.get('q', '').strip()
    conduta_filtro = request.GET.get('conduta', '').strip()
    subunidade_filtro = request.GET.get('subunidade', '').strip()
    post_grad_filtro = request.GET.get('post_grad', '').strip()

    registros_qs = ConstaQue.objects.select_related('post_grad').all()

    if conduta_filtro:
        registros_qs = registros_qs.filter(conduta=conduta_filtro)

    if subunidade_filtro:
        registros_qs = registros_qs.filter(subunidade=subunidade_filtro)

    if post_grad_filtro:
        registros_qs = registros_qs.filter(post_grad_id=post_grad_filtro)

    if query:
        condutas_encontradas = [
            chave for chave, label in ConstaQue.CONDUTA_CHOICES
            if query.lower() in label.lower()
        ]

        subunidades_encontradas = [
            chave for chave, label in ConstaQue.SUBUNIDADE_CHOICES
            if query.lower() in label.lower()
        ]

        registros_qs = registros_qs.filter(
            Q(re__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(nome_completo__icontains=query) |
            Q(post_grad__title__icontains=query) |
            Q(subunidade__icontains=query) |
            Q(subunidade__in=subunidades_encontradas) |
            Q(consulta__icontains=query) |
            Q(p2__icontains=query) |
            Q(jd__icontains=query) |
            Q(observacao__icontains=query) |
            Q(conduta__icontains=query) |
            Q(conduta__in=condutas_encontradas)
        )

    paginator = Paginator(registros_qs, 25)
    page_number = request.GET.get('page')
    registros = paginator.get_page(page_number)

    context = {
        'registros': registros,
        'query': query,
        'conduta_filtro': conduta_filtro,
        'subunidade_filtro': subunidade_filtro,
        'post_grad_filtro': post_grad_filtro,
        'conduta_choices': ConstaQue.CONDUTA_CHOICES,
        'subunidade_choices': ConstaQue.SUBUNIDADE_CHOICES,
        'post_grad_choices': PostGrad.objects.all(),
    }

    return render(request, 'consta_que.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from.models import PlanoChamada


@login_required
@permission_required('planochamada.view_material', raise_exception=True)
def plano_chamada_list(request):

    query = request.GET.get('q', '').strip()
    policiais_qs = PlanoChamada.objects.select_related('post_grad').all()

    if query:
        policiais_qs = policiais_qs.filter(
            Q(re__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(nome_completo__icontains=query) |
            Q(post_grad__title__icontains=query) |
            Q(subunidade__icontains=query) |
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
    }

    return render(request, 'policiais.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Material


@login_required
@permission_required('material.view_material', raise_exception=True)
def home(request):

    query = request.GET.get('q', '').strip()
    materials_list = Material.objects.all()

    if query:
        materials_list = materials_list.filter(
            Q(controle_aa__icontains=query) |
            Q(nome__icontains=query) |
            Q(patrimonio__icontains=query) |
            Q(localizacao__icontains=query) |
            Q(recibo__icontains=query) |
            Q(observacao__icontains=query)
        )

    paginator = Paginator(materials_list, 25)

    page_number = request.GET.get('page')
    materials = paginator.get_page(page_number)

    context = {
        'materials': materials,
        'query': query,
    }

    return render(request, 'materials.html', context)

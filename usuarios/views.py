from urllib.parse import urlparse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import login, logout
from .forms import CustomAuthenticationForm


def _obter_url_retorno(request, fallback='/'):
    # 1. Tenta pegar via ?next= (GET ou POST)
    next_url = request.GET.get('next') or request.POST.get('next')

    # 2. Se não houver ?next=, tenta pegar a página anterior (HTTP_REFERER)
    if not next_url:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            parsed = urlparse(referer)
            # Evita loop redirecionando de volta para a própria tela de login
            if parsed.path != request.path:
                next_url = referer

    # 3. Valida se a URL pertence ao mesmo domínio (segurança contra Open Redirect)
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return fallback


def custom_admin_login_view(request):
    next_url = _obter_url_retorno(request, fallback='/')

    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login realizado com sucesso.')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'next': next_url,
    }

    return render(request, 'login.html', context)


def custom_admin_logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema com sucesso.')
    return redirect('/admin/login/')
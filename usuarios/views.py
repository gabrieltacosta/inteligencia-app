from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import login, logout
from .forms import CustomAuthenticationForm


def custom_admin_login_view(request):

    if request.user.is_authenticated:
        return redirect('/inventario/')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login realizado com sucesso.')
            next_url = request.GET.get('next') or request.POST.get('next') 
            if not next_url or not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                next_url = '/inventario/'
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'next': request.GET.get('next') or request.POST.get('next', ''),
    }    

    return render(request, 'login.html', context)

def custom_admin_logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema com sucesso.')
    return redirect('/admin/login/')
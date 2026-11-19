from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import custom_admin_login_view

admin.site.site_header = "6º BPRv Inteligência - Administração"
admin.site.site_title = "6º BPRv - Inteligência"
admin.site.index_title = "Bem-vindo ao portal de gestão"

urlpatterns = [
    path('admin/login/', custom_admin_login_view, name='admin_login'),
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('inventario/', include('material.urls')),
    path('policiais/', include('policial.urls')),
    path('usuarios/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns += [
        path('teste-403/', lambda request: render(request, '403.html')),
        path('teste-404/', lambda request: render(request, '404.html')),
        path('teste-500/', lambda request: render(request, '500.html')),
    ]
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import custom_admin_login_view

urlpatterns = [
    path('admin/login/', custom_admin_login_view, name='admin_login'),
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('inventario/', include('material.urls')),
    path('usuarios/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
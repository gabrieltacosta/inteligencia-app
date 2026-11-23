from django.urls import path
from . import views

app_name = 'material'

urlpatterns = [
    path('inventario/', views.home, name='home'),
    path('qr/<str:material_id>/', views.material_qr_detalhe, name="qr_detalhe")
]

from django.urls import path
from . import views

app_name = 'policial'

urlpatterns = [
    path('plano-chamada/', views.plano_chamada_list, name='plano_chamada_list'),
    path('consta-que/', views.consta_que_list, name='consta_que_list'),
]

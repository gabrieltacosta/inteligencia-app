from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('logout/', views.custom_admin_logout_view, name='admin_logout'),
]

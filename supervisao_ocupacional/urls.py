# supervisao_ocupacional/urls.py
from django.urls import path
from .views_modules.base_views import index
from .views_modules.laudos_views import laudos
from .views_modules.documentospgt_views import documentospgt
from .views_modules.docs_recebidos_views import docs_recebidos
from .views_modules.pareceres_views import pareceres
from .views_modules.planilhas_views import planilhas

# Adicione esta linha para definir o namespace
app_name = 'supervisao_ocupacional'

urlpatterns = [
    path('', index, name='index'),
    path('laudos/', laudos, name='laudos'),
    path('documentospgt/', documentospgt, name='documentospgt'),
    path('docs_recebidos/', docs_recebidos, name='docs_recebidos'),
    path('pareceres/', pareceres, name='pareceres'),
    path('planilhas/', planilhas, name='planilhas'),
]

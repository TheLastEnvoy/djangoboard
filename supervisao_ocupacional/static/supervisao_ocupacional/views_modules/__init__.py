# supervisao_ocupacional/views_modules/__init__.py
# Importações absolutas para evitar problemas
from supervisao_ocupacional.views_modules.base_views import remove_special_chars, load_data, index
from supervisao_ocupacional.views_modules.laudos_views import laudos
from supervisao_ocupacional.views_modules.documentospgt_views import documentospgt
from supervisao_ocupacional.views_modules.docs_recebidos_views import docs_recebidos
from supervisao_ocupacional.views_modules.pareceres_views import pareceres
from supervisao_ocupacional.views_modules.planilhas_views import planilhas

# Definir quais símbolos são exportados quando alguém faz "from views_modules import *"
__all__ = [
    'remove_special_chars', 
    'load_data', 
    'index',
    'laudos', 
    'documentospgt', 
    'docs_recebidos', 
    'pareceres', 
    'planilhas'
]

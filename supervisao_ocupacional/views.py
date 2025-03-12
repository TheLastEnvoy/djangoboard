# supervisao_ocupacional/views.py
"""
Este arquivo contém apenas redirecionamentos para as views modulares.
"""

# Funções auxiliares
def remove_special_chars(text):
    from supervisao_ocupacional.views_modules.base_views import remove_special_chars
    return remove_special_chars(text)

def load_data(file_name):
    from supervisao_ocupacional.views_modules.base_views import load_data
    return load_data(file_name)

# Views principais
def index(request):
    from supervisao_ocupacional.views_modules.base_views import index
    return index(request)

def laudos(request):
    from supervisao_ocupacional.views_modules.laudos_views import laudos
    return laudos(request)

def documentospgt(request):
    from supervisao_ocupacional.views_modules.documentospgt_views import documentospgt
    return documentospgt(request)

def docs_recebidos(request):
    from supervisao_ocupacional.views_modules.docs_recebidos_views import docs_recebidos
    return docs_recebidos(request)

def pareceres(request):
    from supervisao_ocupacional.views_modules.pareceres_views import pareceres
    return pareceres(request)

def planilhas(request):
    from supervisao_ocupacional.views_modules.planilhas_views import planilhas
    return planilhas(request)

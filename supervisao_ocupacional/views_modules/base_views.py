# supervisao_ocupacional/views/base_views.py
import os
import pandas as pd
from django.conf import settings
import re
from django.shortcuts import render
from django.db.models import Count
from supervisao_ocupacional.models import Laudo, DocumentoPGT, DocumentoRecebido, Parecer, Planilha

def index(request):
    """View para a página inicial do dashboard."""
    # Contagem de registros em cada modelo
    total_laudos = Laudo.objects.count()
    total_documentos_pgt = DocumentoPGT.objects.count()
    total_documentos_recebidos = DocumentoRecebido.objects.count()
    total_pareceres = Parecer.objects.count()
    total_planilhas = Planilha.objects.count()

    context = {
        'title': 'Dashboard de Supervisão Ocupacional',
        'total_laudos': total_laudos,
        'total_documentos_pgt': total_documentos_pgt,
        'total_documentos_recebidos': total_documentos_recebidos,
        'total_pareceres': total_pareceres,
        'total_planilhas': total_planilhas,
    }

    return render(request, 'supervisao_ocupacional/index.html', context)

def load_data(filename):
    """
    Carrega dados de uma planilha Excel.
    Esta função é mantida para compatibilidade com código existente,
    mas o ideal é usar os modelos do Django para acessar os dados.
    """
    file_path = os.path.join(settings.BASE_DIR, 'supervisao_ocupacional', 'data', filename)
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Erro ao carregar o arquivo {filename}: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

def remove_special_chars(text):
    """
    Remove caracteres especiais de um texto.
    Útil para normalizar nomes de municípios, assentamentos, etc.
    """
    if not isinstance(text, str):
        return text

    # Manter apenas letras, números e espaços
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def format_date(date):
    """
    Formata uma data para exibição no formato DD/MM/YYYY.
    """
    if pd.isna(date) or date is None:
        return ""

    try:
        if isinstance(date, str):
            # Tentar converter string para data
            date = pd.to_datetime(date)

        # Formatar data
        return date.strftime('%d/%m/%Y')
    except:
        return str(date)

def get_color_for_percentage(percentage):
    """
    Retorna uma cor baseada em um percentual.
    Útil para indicadores visuais em dashboards.

    Vermelho (<30%), Amarelo (30-70%), Verde (>70%)
    """
    if percentage < 30:
        return "danger"  # Vermelho
    elif percentage < 70:
        return "warning"  # Amarelo
    else:
        return "success"  # Verde

def convert_queryset_to_dataframe(queryset, field_mapping=None):
    """
    Converte um queryset do Django para um DataFrame do pandas.
    Opcionalmente renomeia os campos de acordo com o mapeamento fornecido.

    Args:
        queryset: O queryset a ser convertido
        field_mapping: Dicionário com mapeamento {nome_campo_modelo: nome_campo_dataframe}

    Returns:
        DataFrame do pandas
    """
    # Converter queryset para lista de dicionários
    data = list(queryset.values())

    # Criar DataFrame
    df = pd.DataFrame(data)

    # Renomear campos se necessário
    if field_mapping and not df.empty:
        # Aplicar renomeação apenas para colunas que existem no DataFrame
        rename_dict = {k: v for k, v in field_mapping.items() if k in df.columns}
        if rename_dict:
            df = df.rename(columns=rename_dict)

    return df

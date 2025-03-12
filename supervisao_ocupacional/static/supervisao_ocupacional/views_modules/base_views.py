# supervisao_ocupacional/views_modules/base_views.py
import os
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from django.conf import settings
import unicodedata

def remove_special_chars(text):
    """Remove caracteres especiais e normaliza texto."""
    if not isinstance(text, str):
        return text  # Retorna o valor original se não for uma string
    return ''.join(ch for ch in unicodedata.normalize('NFKD', str(text)) 
                  if not unicodedata.combining(ch))

def load_data(file_name):
    """Carrega os dados do arquivo Excel."""
    try:
        file_path = os.path.join(settings.BASE_DIR, 'supervisao_ocupacional', 'data', file_name)
        print(f"Tentando carregar arquivo: {file_path}")

        if not os.path.exists(file_path):
            print(f"ERRO: Arquivo não encontrado: {file_path}")
            # Criar um DataFrame vazio com as colunas esperadas
            return pd.DataFrame(columns=[
                'Código SIPRA', 'Município', 'Assentamento', 'Lote', 'Arquivo',
                'Tipo de Laudo', 'Data', 'Técnico', 'Modalidade'
            ])

        # Carregar o arquivo Excel
        df = pd.read_excel(file_path)
        print(f"Arquivo carregado com sucesso. {len(df)} registros encontrados.")
        print(f"Colunas disponíveis: {df.columns.tolist()}")

        return df

    except Exception as e:
        print(f"ERRO ao carregar arquivo: {e}")
        # Retornar DataFrame vazio em caso de erro
        return pd.DataFrame(columns=[
            'Código SIPRA', 'Município', 'Assentamento', 'Lote', 'Arquivo',
            'Tipo de Laudo', 'Data', 'Técnico', 'Modalidade'
        ])

def index(request):
    """View para a página inicial."""
    # Carregar dados
    laudos_df = load_data('01_laudos_SO_infos.xlsx')
    documentospgt_df = load_data('02_contPGT.xlsx')
    docs_recebidos_df = load_data('03_contDocsRecebidos.xlsx')
    pareceres_df = load_data('04_contPareceres.xlsx')
    planilhas_df = load_data('05_contPlanilhas.xlsx')

    # Calcular estatísticas
    total_laudos = len(laudos_df)
    total_documentospgt = len(documentospgt_df)
    total_docs_recebidos = len(docs_recebidos_df)
    total_pareceres = len(pareceres_df)
    total_planilhas = len(planilhas_df)

    # Criar gráfico de barras para o total de cada categoria
    categorias = ['Laudos', 'Documentos PGT', 'Docs Recebidos', 'Pareceres', 'Planilhas']
    valores = [total_laudos, total_documentospgt, total_docs_recebidos, total_pareceres, total_planilhas]

    fig = px.bar(
        x=categorias,
        y=valores,
        title='Total por Categoria',
        labels={'x': 'Categoria', 'y': 'Total'},
        color_discrete_sequence=['#1f77b4']
    )

    fig.update_layout(
        xaxis_title="Categoria",
        yaxis_title="Total",
        bargap=0.2,
        bargroupgap=0.1
    )

    chart_json = fig.to_json()

    context = {
        'title': 'Dashboard de Supervisão Ocupacional',
        'total_laudos': total_laudos,
        'total_documentospgt': total_documentospgt,
        'total_docs_recebidos': total_docs_recebidos,
        'total_pareceres': total_pareceres,
        'total_planilhas': total_planilhas,
        'chart_json': chart_json,
    }

    return render(request, 'supervisao_ocupacional/index.html', context)

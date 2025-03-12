# supervisao_ocupacional/views/pareceres_views.py
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from .base_views import load_data

def pareceres(request):
    """View para o dashboard de pareceres."""
    # Carregar dados
    try:
        df = load_data('04_contPareceres.xlsx')
    except:
        # Caso o arquivo não exista, crie um DataFrame vazio
        df = pd.DataFrame()

    # Preencher valores vazios se o DataFrame não estiver vazio
    if not df.empty:
        if 'Município' in df.columns:
            df['Município'] = df['Município'].fillna('Desconhecido')

        # Preparar listas para filtros
        municipios = ['Todos']
        if 'Município' in df.columns:
            municipios += sorted(list(df['Município'].unique()))

        # Aplicar filtros do request
        filtered_df = df.copy()
        municipio_filtro = request.GET.get('municipio', 'Todos')

        if municipio_filtro != 'Todos' and 'Município' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Município'] == municipio_filtro]

        # Gráficos e estatísticas
        total_pareceres = len(filtered_df)

        # Converter DataFrame para lista de dicionários para o template
        pareceres_list = filtered_df.to_dict('records')

        # Gráfico de pizza - Distribuição por município (se a coluna existir)
        municipio_chart = None
        if 'Município' in filtered_df.columns:
            municipio_counts = filtered_df['Município'].value_counts()
            if len(municipio_counts) > 0:
                fig_municipio = px.pie(
                    names=municipio_counts.index,
                    values=municipio_counts.values,
                    title='Distribuição dos Pareceres por Município'
                )
                fig_municipio.update_traces(textposition='inside', textinfo='percent+label')
                municipio_chart = fig_municipio.to_json()
    else:
        # Valores padrão se o DataFrame estiver vazio
        municipios = ['Todos']
        municipio_filtro = 'Todos'
        total_pareceres = 0
        pareceres_list = []
        municipio_chart = None

    context = {
        'title': 'Dashboard de Pareceres',
        'pareceres': pareceres_list,
        'total_pareceres': total_pareceres,
        'municipios': municipios,
        'municipio_filtro': municipio_filtro,
        'municipio_chart': municipio_chart,
    }

    return render(request, 'supervisao_ocupacional/pareceres.html', context)

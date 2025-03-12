# supervisao_ocupacional/views/planilhas_views.py
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from supervisao_ocupacional.views_modules.base_views import load_data

def planilhas(request):
    """View para o dashboard de planilhas."""
    # Carregar dados
    try:
        df = load_data('05_contPlanilhas.xlsx')
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
        total_planilhas = len(filtered_df)

        # Converter DataFrame para lista de dicionários para o template
        planilhas_list = filtered_df.to_dict('records')

        # Gráfico de pizza - Distribuição por município (se a coluna existir)
        municipio_chart = None
        if 'Município' in filtered_df.columns:
            municipio_counts = filtered_df['Município'].value_counts()
            if len(municipio_counts) > 0:
                fig_municipio = px.pie(
                    names=municipio_counts.index,
                    values=municipio_counts.values,
                    title='Distribuição das Planilhas por Município'
                )
                fig_municipio.update_traces(textposition='inside', textinfo='percent+label')
                municipio_chart = fig_municipio.to_json()
    else:
        # Valores padrão se o DataFrame estiver vazio
        municipios = ['Todos']
        municipio_filtro = 'Todos'
        total_planilhas = 0
        planilhas_list = []
        municipio_chart = None

    context = {
        'title': 'Dashboard de Planilhas',
        'planilhas': planilhas_list,
        'total_planilhas': total_planilhas,
        'municipios': municipios,
        'municipio_filtro': municipio_filtro,
        'municipio_chart': municipio_chart,
    }

    return render(request, 'supervisao_ocupacional/planilhas.html', context)

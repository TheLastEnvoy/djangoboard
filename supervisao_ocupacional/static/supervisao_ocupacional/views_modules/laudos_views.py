# supervisao_ocupacional/views/laudos_views.py
import pandas as pd
import plotly.express as px
from django.shortcuts import render
import numpy as np
from datetime import datetime
from supervisao_ocupacional.views_modules.base_views import load_data, remove_special_chars

def laudos(request):
    """View para o dashboard de laudos."""
    # Carregar dados
    df = load_data('01_laudos_SO_infos.xlsx')

    # Verificar se as colunas esperadas existem
    expected_columns = [
        'Código SIPRA', 'Município', 'Assentamento', 'Lote', 'Arquivo',
        'Tipo de Laudo', 'Data', 'Técnico', 'Modalidade'
    ]

    for col in expected_columns:
        if col not in df.columns:
            print(f"AVISO: Coluna '{col}' não encontrada no DataFrame")

    # Preencher valores vazios
    df['Modalidade'] = df['Modalidade'].fillna('Desconhecido')
    df['Município'] = df['Município'].fillna('Desconhecido')
    df['Assentamento'] = df['Assentamento'].fillna('Desconhecido')
    df['Tipo de Laudo'] = df['Tipo de Laudo'].fillna('Desconhecido')

    # Aplicar a função para remover caracteres especiais
    df['Município'] = df['Município'].apply(remove_special_chars)

    # Converter coluna de data
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    # Remover registros com datas inválidas
    df = df.dropna(subset=['Data'])

    # Filtros
    tecnicos = ['Todos'] + sorted(list(df['Técnico'].unique()))
    municipios = ['Todos'] + sorted(list(df['Município'].unique()))
    assentamentos = ['Todos'] + sorted(list(df['Assentamento'].unique()))
    tipos_de_laudo = ['Todos'] + sorted(list(df['Tipo de Laudo'].unique()))
    modalidades = ['Todos'] + sorted(list(df['Modalidade'].unique()))

    # Aplicar filtros do request
    filtered_df = df.copy()

    tecnico_filtro = request.GET.get('tecnico', 'Todos')
    municipio_filtro = request.GET.get('municipio', 'Todos')
    assentamento_filtro = request.GET.get('assentamento', 'Todos')
    tipo_laudo_filtro = request.GET.get('tipo_laudo', 'Todos')
    modalidade_filtro = request.GET.get('modalidade', 'Todos')

    if tecnico_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Técnico'] == tecnico_filtro]

    if municipio_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Município'] == municipio_filtro]

    if assentamento_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Assentamento'] == assentamento_filtro]

    if tipo_laudo_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Tipo de Laudo'] == tipo_laudo_filtro]

    if modalidade_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Modalidade'] == modalidade_filtro]

    # Calcular estatísticas - CORREÇÃO: Melhorar a filtragem das modalidades
    # Normalizar a coluna Modalidade para comparação
    df['Modalidade_Norm'] = df['Modalidade'].str.upper().str.strip()

    # Usar valores reais da planilha para as modalidades com filtragem melhorada
    vistoria_df = df[df['Modalidade_Norm'].str.contains('VISTORIA', na=False)]
    mutirao_df = df[df['Modalidade_Norm'].str.contains('MUTIR', na=False)]  # Captura "MUTIRÃO", "MUTIRAO", etc.

    total_vistoria = len(vistoria_df)
    total_mutirao = len(mutirao_df)

    # Meta total para cada modalidade (valores fixos conforme a imagem)
    meta_vistoria = 4739
    meta_mutirao = 2746

    # Calcular percentuais
    percentual_vistoria = (total_vistoria / meta_vistoria) * 100 if meta_vistoria > 0 else 0
    percentual_mutirao = (total_mutirao / meta_mutirao) * 100 if meta_mutirao > 0 else 0

    # Limitar percentuais a 100%
    percentual_vistoria = min(percentual_vistoria, 100)
    percentual_mutirao = min(percentual_mutirao, 100)

    # Gráfico de pizza - Distribuição por município
    municipio_counts = filtered_df['Município'].value_counts()
    # Garantir que temos pelo menos alguns municípios para mostrar
    if len(municipio_counts) > 0:
        # Limitar a 15 municípios mais frequentes para melhor visualização
        if len(municipio_counts) > 15:
            outros_count = municipio_counts[15:].sum()
            municipio_counts = municipio_counts[:15]
            municipio_counts['Outros'] = outros_count

        fig_municipio = px.pie(
            names=municipio_counts.index,
            values=municipio_counts.values,
            title='Distribuição dos Laudos por Município',
            hole=0.3,  # Donut chart
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_municipio.update_traces(textposition='inside', textinfo='percent+label')
        fig_municipio.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
        )
    else:
        # Gráfico vazio se não houver dados
        fig_municipio = px.pie(
            names=['Sem dados'],
            values=[1],
            title='Distribuição dos Laudos por Município'
        )

    municipio_chart = fig_municipio.to_json()

    # Gráficos de barras por mês para diferentes anos - CORREÇÃO: Melhorar a visualização mensal
    anos = [2023, 2024, 2025]
    mensal_charts = {}

    for ano in anos:
        df_ano = filtered_df[filtered_df['Data'].dt.year == ano]

        # CORREÇÃO: Usar resample para agrupar corretamente por mês
        if not df_ano.empty:
            # Configurar o índice como a data para usar resample
            df_temp = df_ano.set_index('Data')
            # Agrupar por mês e contar
            laudos_por_mes = df_temp.resample('M').size()
            # Converter o índice para número do mês (1-12)
            laudos_por_mes.index = laudos_por_mes.index.month
        else:
            # Se não houver dados para o ano, criar série vazia
            laudos_por_mes = pd.Series(dtype='int64')

        # Garantir que todos os meses estão representados (1-12)
        todos_meses = pd.Series(0, index=range(1, 13))
        laudos_por_mes = laudos_por_mes.combine_first(todos_meses).sort_index()

        # Converter números dos meses para nomes
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        fig_mensal = px.bar(
            x=meses,
            y=laudos_por_mes.values,
            title=f'Quantidade de Laudos por Mês em {ano}',
            labels={'x': 'Mês', 'y': 'Quantidade de Laudos'},
            color_discrete_sequence=['#1f77b4']  # Cor azul consistente
        )
        fig_mensal.update_layout(
            xaxis_title="Mês",
            yaxis_title="Quantidade de Laudos",
            bargap=0.2,
            bargroupgap=0.1
        )
        mensal_charts[ano] = fig_mensal.to_json()

    # Gráfico de pizza - tipo de laudo
    tipo_laudo_counts = filtered_df['Tipo de Laudo'].value_counts()

    if len(tipo_laudo_counts) > 0:
        # Limitar a 10 tipos mais frequentes para melhor visualização
        if len(tipo_laudo_counts) > 10:
            outros_count = tipo_laudo_counts[10:].sum()
            tipo_laudo_counts = tipo_laudo_counts[:10]
            tipo_laudo_counts['Outros'] = outros_count

        fig_tipo_laudo = px.pie(
            names=tipo_laudo_counts.index,
            values=tipo_laudo_counts.values,
            title='Distribuição dos Laudos por Tipo',
            hole=0.3,  # Donut chart
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_tipo_laudo.update_traces(textposition='inside', textinfo='percent+label')
        fig_tipo_laudo.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
        )
    else:
        # Gráfico vazio se não houver dados
        fig_tipo_laudo = px.pie(
            names=['Sem dados'],
            values=[1],
            title='Distribuição dos Laudos por Tipo'
        )

    tipo_laudo_chart = fig_tipo_laudo.to_json()

    # Calcular o total de laudos para cada tipo de laudo - CORREÇÃO: Ajustar nomes de colunas
    total_por_tipo_laudo = filtered_df['Tipo de Laudo'].value_counts().reset_index()
    total_por_tipo_laudo.columns = ['Tipo_de_Laudo', 'Quantidade']

    # Adicionar linha de total
    total_laudos = total_por_tipo_laudo['Quantidade'].sum()
    total_por_tipo_laudo.loc[len(total_por_tipo_laudo)] = ['Total', total_laudos]

    # CORREÇÃO: Ajustar o DataFrame para o template
    # Renomear a coluna 'Tipo de Laudo' para 'Tipo_de_Laudo' no DataFrame principal
    filtered_df_for_template = filtered_df.copy()
    if 'Tipo de Laudo' in filtered_df_for_template.columns:
        filtered_df_for_template['Tipo_de_Laudo'] = filtered_df_for_template['Tipo de Laudo']

    # Converter DataFrame para lista de dicionários para o template
    laudos_list = filtered_df_for_template.to_dict('records')
    tipos_laudo_list = total_por_tipo_laudo.to_dict('records')

    context = {
        'title': 'Dashboard de Laudos',
        'laudos': laudos_list,
        'total_laudos': len(filtered_df),
        'total_vistoria': total_vistoria,
        'total_mutirao': total_mutirao,
        'meta_vistoria': meta_vistoria,
        'meta_mutirao': meta_mutirao,
        'percentual_vistoria': percentual_vistoria,
        'percentual_mutirao': percentual_mutirao,
        'tecnicos': tecnicos,
        'municipios': municipios,
        'assentamentos': assentamentos,
        'tipos_de_laudo': tipos_de_laudo,
        'modalidades': modalidades,
        'tecnico_filtro': tecnico_filtro,
        'municipio_filtro': municipio_filtro,
        'assentamento_filtro': assentamento_filtro,
        'tipo_laudo_filtro': tipo_laudo_filtro,
        'modalidade_filtro': modalidade_filtro,
        'municipio_chart': municipio_chart,
        'mensal_chart_2023': mensal_charts[2023],
        'mensal_chart_2024': mensal_charts[2024],
        'mensal_chart_2025': mensal_charts[2025],
        'tipo_laudo_chart': tipo_laudo_chart,
        'tipos_laudo_list': tipos_laudo_list,
    }

    return render(request, 'supervisao_ocupacional/laudos.html', context)

# supervisao_ocupacional/views/pareceres_views.py
import json
import logging
from django.shortcuts import render
from django.http import HttpRequest
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supervisao_ocupacional.views_modules.base_views import load_data

logger = logging.getLogger(__name__)

def pareceres(request: HttpRequest):
    """
    View para o dashboard de pareceres conclusivos.

    Exibe métricas, gráficos e dados detalhados sobre pareceres padrão e de desbloqueio.
    """
    context = {
        'title': 'Dashboard de Pareceres',
    }

    try:
        # Carregar dados
        df = load_data('04_contPareceres.xlsx')

        if df.empty:
            return _render_empty_dashboard(request, context)

        # Preencher valores vazios
        df = _preprocess_dataframe(df)

        # Preparar listas para filtros
        filtros = _prepare_filter_options(df)
        context.update(filtros)

        # Aplicar filtros do request
        filtered_df = _apply_filters(df, request)

        # Calcular métricas
        metricas = _calculate_metrics(filtered_df)
        context.update(metricas)

        # Gerar gráficos
        graficos = _generate_charts(filtered_df)
        context.update(graficos)

        # Converter DataFrame para lista de dicionários para o template
        context['pareceres'] = filtered_df.to_dict('records')

    except Exception as e:
        logger.error(f"Erro ao processar dashboard de pareceres: {str(e)}")
        context['error_message'] = "Ocorreu um erro ao carregar os dados. Por favor, tente novamente mais tarde."
        return _render_empty_dashboard(request, context)

    return render(request, 'supervisao_ocupacional/pareceres.html', context)

def _preprocess_dataframe(df):
    """Pré-processa o DataFrame, preenchendo valores nulos e garantindo consistência."""
    # Preencher valores vazios
    for col in ['Município', 'Assentamento', 'Tipo']:
        if col in df.columns:
            df[col] = df[col].fillna('Desconhecido')

    return df

def _prepare_filter_options(df):
    """Prepara as opções de filtro para o dashboard."""
    filtros = {}

    # Opções de filtro para Município
    if 'Município' in df.columns:
        filtros['municipios'] = ['Todos'] + sorted(df['Município'].unique().tolist())
    else:
        filtros['municipios'] = ['Todos']

    # Opções de filtro para Assentamento
    if 'Assentamento' in df.columns:
        filtros['assentamentos'] = ['Todos'] + sorted(df['Assentamento'].unique().tolist())
    else:
        filtros['assentamentos'] = ['Todos']

    # Opções de filtro para Tipo
    if 'Tipo' in df.columns:
        filtros['tipos'] = ['Todos'] + sorted(df['Tipo'].unique().tolist())
    else:
        filtros['tipos'] = ['Todos']

    # Valores selecionados
    filtros['municipio_filtro'] = request.GET.get('municipio', 'Todos')
    filtros['assentamento_filtro'] = request.GET.get('assentamento', 'Todos')
    filtros['tipo_filtro'] = request.GET.get('tipo', 'Todos')

    return filtros

def _apply_filters(df, request):
    """Aplica os filtros selecionados pelo usuário ao DataFrame."""
    filtered_df = df.copy()

    # Filtro por município
    municipio_filtro = request.GET.get('municipio', 'Todos')
    if municipio_filtro != 'Todos' and 'Município' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Município'] == municipio_filtro]

    # Filtro por assentamento
    assentamento_filtro = request.GET.get('assentamento', 'Todos')
    if assentamento_filtro != 'Todos' and 'Assentamento' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Assentamento'] == assentamento_filtro]

    # Filtro por tipo
    tipo_filtro = request.GET.get('tipo', 'Todos')
    if tipo_filtro != 'Todos' and 'Tipo' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Tipo'] == tipo_filtro]

    return filtered_df

def _calculate_metrics(df):
    """Calcula as métricas para o dashboard."""
    metricas = {
        'total_pareceres': len(df)
    }

    # Métricas por tipo de parecer
    if 'Tipo' in df.columns:
        # Total de pareceres padrão
        padrao_total = len(df[df['Tipo'] == 'Padrão'])
        total_padrao = 4239  # Meta total de pareceres padrão
        percentual_padrao = (padrao_total / total_padrao) * 100 if total_padrao > 0 else 0

        # Total de pareceres de desbloqueio
        desbloqueio_total = len(df[df['Tipo'] == 'Desbloqueio'])
        total_desbloqueio = 500  # Meta total de pareceres de desbloqueio
        percentual_desbloqueio = (desbloqueio_total / total_desbloqueio) * 100 if total_desbloqueio > 0 else 0

        metricas.update({
            'padrao_total': padrao_total,
            'total_padrao': total_padrao,
            'percentual_padrao': round(percentual_padrao, 1),
            'desbloqueio_total': desbloqueio_total,
            'total_desbloqueio': total_desbloqueio,
            'percentual_desbloqueio': round(percentual_desbloqueio, 1),
        })

    return metricas

def _generate_charts(df):
    """Gera os gráficos para o dashboard."""
    charts = {}

    # Gráfico de distribuição por tipo
    if 'Tipo' in df.columns and not df['Tipo'].empty:
        tipo_counts = df['Tipo'].value_counts()
        if len(tipo_counts) > 0:
            fig_tipo = px.pie(
                names=tipo_counts.index,
                values=tipo_counts.values,
                title='Distribuição por Tipo',
                color_discrete_map={'Padrão': 'lightblue', 'Desbloqueio': 'coral'}
            )
            fig_tipo.update_traces(textposition='inside', textinfo='percent+label')
            # Converter para HTML em vez de JSON
            charts['tipo_chart_div'] = fig_tipo.to_html(full_html=False, include_plotlyjs=False)

    # Gráfico de distribuição por assentamento
    if 'Assentamento' in df.columns and not df['Assentamento'].empty:
        assentamento_counts = df['Assentamento'].value_counts()
        if len(assentamento_counts) > 0:
            fig_assentamento = px.pie(
                names=assentamento_counts.index,
                values=assentamento_counts.values,
                title='Distribuição por Assentamento'
            )
            fig_assentamento.update_traces(textposition='inside', textinfo='percent+label')
            # Converter para HTML em vez de JSON
            charts['assentamento_chart_div'] = fig_assentamento.to_html(full_html=False, include_plotlyjs=False)

    # Gráfico de distribuição por município
    if 'Município' in df.columns and not df['Município'].empty:
        municipio_counts = df['Município'].value_counts()
        if len(municipio_counts) > 0:
            fig_municipio = px.pie(
                names=municipio_counts.index,
                values=municipio_counts.values,
                title='Distribuição por Município'
            )
            fig_municipio.update_traces(textposition='inside', textinfo='percent+label')
            # Converter para HTML em vez de JSON
            charts['municipio_chart_div'] = fig_municipio.to_html(full_html=False, include_plotlyjs=False)

    return charts

def _render_empty_dashboard(request, context):
    """Renderiza o dashboard com valores padrão quando não há dados disponíveis."""
    context.update({
        'municipios': ['Todos'],
        'assentamentos': ['Todos'],
        'tipos': ['Todos'],
        'municipio_filtro': 'Todos',
        'assentamento_filtro': 'Todos',
        'tipo_filtro': 'Todos',
        'total_pareceres': 0,
        'padrao_total': 0,
        'total_padrao': 4239,
        'percentual_padrao': 0,
        'desbloqueio_total': 0,
        'total_desbloqueio': 500,
        'percentual_desbloqueio': 0,
        'pareceres': [],
        'tipo_chart_div': None,
        'assentamento_chart_div': None,
        'municipio_chart_div': None,
    })

    return render(request, 'supervisao_ocupacional/pareceres.html', context)

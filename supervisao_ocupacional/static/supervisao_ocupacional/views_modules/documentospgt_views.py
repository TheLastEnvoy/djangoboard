# supervisao_ocupacional/views/documentos_views.py
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from supervisao_ocupacional.views_modules.base_views import load_data

def documentospgt(request):
    """View para o dashboard de documentos (PGT)."""
    # Carregar dados
    df = load_data('02_contPGT.xlsx')

    # Preencher valores vazios
    if 'Objetivo' in df.columns:
        df['Objetivo'] = df['Objetivo'].fillna('Não especificado')

    df['Município'] = df['Município'].fillna('Desconhecido')
    df['Assentamento'] = df['Assentamento'].fillna('Desconhecido')

    # Verificar se a coluna 'Tipo de documento PGT' existe
    if 'Tipo de documento PGT' not in df.columns:
        # Criar um DataFrame vazio com as colunas esperadas
        return render(request, 'supervisao_ocupacional/documentospgt.html', {
            'title': 'Dashboard de Documentos (PGT)',
            'error_message': "A coluna 'Tipo de documento PGT' não está presente nos dados."
        })

    # Preparar listas para filtros
    tipos_documentopgt = ['Todos'] + sorted(list(df['Tipo de documento PGT'].unique()))
    assentamentos = ['Todos'] + sorted(list(df['Assentamento'].unique()))
    municipios = ['Todos'] + sorted(list(df['Município'].unique()))

    if 'Nome T1' in df.columns:
        nomes_t1 = ['Todos'] + sorted(list(df['Nome T1'].unique()))
    else:
        nomes_t1 = ['Todos']

    if 'Objetivo' in df.columns:
        objetivos = ['Todos'] + sorted(list(df['Objetivo'].unique()))
    else:
        objetivos = ['Todos']

    # Aplicar filtros do request
    filtered_df = df.copy()

    tipo_documentopgt_filtro = request.GET.get('tipo_documentopgt', 'Todos')
    assentamento_filtro = request.GET.get('assentamento', 'Todos')
    municipio_filtro = request.GET.get('municipio', 'Todos')
    nome_t1_filtro = request.GET.get('nome_t1', 'Todos')
    objetivo_filtro = request.GET.get('objetivo', 'Todos')

    if tipo_documentopgt_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Tipo de documento PGT'] == tipo_documentopgt_filtro]

    if assentamento_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Assentamento'] == assentamento_filtro]

    if municipio_filtro != 'Todos':
        filtered_df = filtered_df[filtered_df['Município'] == municipio_filtro]

    if nome_t1_filtro != 'Todos' and 'Nome T1' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Nome T1'] == nome_t1_filtro]

    if objetivo_filtro != 'Todos' and 'Objetivo' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Objetivo'] == objetivo_filtro]

    # Calcular estatísticas para barras de progresso
    relatorios_conf_atual = len(df[df['Tipo de documento PGT'] == 'Relatório de conformidades para regularização'])
    solicitacoes_atual = len(df[df['Tipo de documento PGT'] == 'Solicitação de documentação complementar'])
    segundos_relatorios_atual = len(df[df['Tipo de documento PGT'].str.contains('2º Relatório', na=False)])
    analise_reg_atual = len(df[df['Tipo de documento PGT'] == 'Análise para regularização'])

    # Definir metas
    total_relatorios_conf = 2246
    total_solicitacoes = 674
    total_segundos_relatorios = 337
    total_analise_reg = 1622

    # Calcular percentuais
    percentual_relatorios_conf = (relatorios_conf_atual / total_relatorios_conf) * 100 if total_relatorios_conf > 0 else 0
    percentual_solicitacoes = (solicitacoes_atual / total_solicitacoes) * 100 if total_solicitacoes > 0 else 0
    percentual_segundos_relatorios = (segundos_relatorios_atual / total_segundos_relatorios) * 100 if total_segundos_relatorios > 0 else 0
    percentual_analise_reg = (analise_reg_atual / total_analise_reg) * 100 if total_analise_reg > 0 else 0

    # Limitar percentuais a 100%
    percentual_relatorios_conf = min(percentual_relatorios_conf, 100)
    percentual_solicitacoes = min(percentual_solicitacoes, 100)
    percentual_segundos_relatorios = min(percentual_segundos_relatorios, 100)
    percentual_analise_reg = min(percentual_analise_reg, 100)

    # Gráfico de pizza - Distribuição por tipo de documento
    tipo_documentopgt_counts = filtered_df['Tipo de documento PGT'].value_counts()
    if len(tipo_documentopgt_counts) > 0:
        fig_tipo_documentopgt = px.pie(
            names=tipo_documentopgt_counts.index,
            values=tipo_documentopgt_counts.values,
            title='Distribuição dos Documentos por Tipo'
        )
        fig_tipo_documentopgt.update_traces(textposition='inside', textinfo='percent+label')
        fig_tipo_documentopgt.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
        )
    else:
        fig_tipo_documentopgt = px.pie(
            names=['Sem dados'],
            values=[1],
            title='Distribuição dos Documentos por Tipo'
        )
    tipo_documentopgt_chart = fig_tipo_documentopgt.to_json()

    # Gráfico de pizza - Distribuição por município
    municipio_counts = filtered_df['Município'].value_counts()
    if len(municipio_counts) > 0:
        fig_municipio = px.pie(
            names=municipio_counts.index,
            values=municipio_counts.values,
            title='Distribuição dos Documentos por Município'
        )
        fig_municipio.update_traces(textposition='inside', textinfo='percent+label')
        fig_municipio.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
        )
    else:
        fig_municipio = px.pie(
            names=['Sem dados'],
            values=[1],
            title='Distribuição dos Documentos por Município'
        )
    municipio_chart = fig_municipio.to_json()

    # Gráfico de barras - Distribuição por assentamento
    assentamento_counts = filtered_df['Assentamento'].value_counts().reset_index()
    assentamento_counts.columns = ['Assentamento', 'Quantidade']
    if len(assentamento_counts) > 0:
        fig_assentamento = px.bar(
            assentamento_counts,
            x='Assentamento',
            y='Quantidade',
            title='Distribuição dos Documentos por Assentamento'
        )
        fig_assentamento.update_layout(
            xaxis_title="Assentamento",
            yaxis_title="Quantidade",
            bargap=0.2,
            bargroupgap=0.1
        )
    else:
        fig_assentamento = px.bar(
            x=['Sem dados'],
            y=[0],
            title='Distribuição dos Documentos por Assentamento'
        )
    assentamento_chart = fig_assentamento.to_json()

    # Gráfico de barras - Distribuição por objetivo (se existir)
    objetivo_chart = None
    if 'Objetivo' in filtered_df.columns:
        objetivo_counts = filtered_df['Objetivo'].value_counts().reset_index()
        objetivo_counts.columns = ['Objetivo', 'Quantidade']
        if len(objetivo_counts) > 0:
            fig_objetivo = px.bar(
                objetivo_counts,
                x='Objetivo',
                y='Quantidade',
                title='Distribuição dos Documentos por Objetivo'
            )
            fig_objetivo.update_layout(
                xaxis_title="Objetivo",
                yaxis_title="Quantidade",
                bargap=0.2,
                bargroupgap=0.1
            )
            objetivo_chart = fig_objetivo.to_json()

    # Tabela de quantidade por tipo e assentamento
    total_por_tipo_assentamento = filtered_df.groupby(['Tipo de documento PGT', 'Assentamento']).size().reset_index(name='Quantidade')
    tipo_assentamento_list = total_por_tipo_assentamento.to_dict('records')

    # Converter DataFrame para lista de dicionários para o template
    documentospgt_list = filtered_df.to_dict('records')

    context = {
        'title': 'Dashboard de Documentos (PGT)',
        'documentospgt': documentospgt_list,
        'total_documentospgt': len(filtered_df),
        'tipos_documentopgt': tipos_documentopgt,
        'assentamentos': assentamentos,
        'municipios': municipios,
        'nomes_t1': nomes_t1,
        'objetivos': objetivos,
        'tipo_documentopgt_filtro': tipo_documentopgt_filtro,
        'assentamento_filtro': assentamento_filtro,
        'municipio_filtro': municipio_filtro,
        'nome_t1_filtro': nome_t1_filtro,
        'objetivo_filtro': objetivo_filtro,
        'relatorios_conf_atual': relatorios_conf_atual,
        'solicitacoes_atual': solicitacoes_atual,
        'segundos_relatorios_atual': segundos_relatorios_atual,
        'analise_reg_atual': analise_reg_atual,
        'total_relatorios_conf': total_relatorios_conf,
        'total_solicitacoes': total_solicitacoes,
        'total_segundos_relatorios': total_segundos_relatorios,
        'total_analise_reg': total_analise_reg,
        'percentual_relatorios_conf': percentual_relatorios_conf,
        'percentual_solicitacoes': percentual_solicitacoes,
        'percentual_segundos_relatorios': percentual_segundos_relatorios,
        'percentual_analise_reg': percentual_analise_reg,
        'tipo_documentopgt_chart': tipo_documentopgt_chart,
        'municipio_chart': municipio_chart,
        'assentamento_chart': assentamento_chart,
        'objetivo_chart': objetivo_chart,
        'tipo_assentamento_list': tipo_assentamento_list,
    }

    return render(request, 'supervisao_ocupacional/documentospgt.html', context)

# supervisao_ocupacional/views/laudos_views.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone
from supervisao_ocupacional.models import Laudo

def laudos(request):
    """View para o dashboard de laudos."""
    # Carregar dados do banco de dados
    queryset = Laudo.objects.all()

    # Aplicar filtros do request
    tecnico_filtro = request.GET.get('tecnico', 'Todos')
    municipio_filtro = request.GET.get('municipio', 'Todos')
    assentamento_filtro = request.GET.get('assentamento', 'Todos')
    tipo_laudo_filtro = request.GET.get('tipo_laudo', 'Todos')
    modalidade_filtro = request.GET.get('modalidade', 'Todos')

    # Aplicar filtros à consulta
    if tecnico_filtro != 'Todos':
        queryset = queryset.filter(tecnico=tecnico_filtro)

    if municipio_filtro != 'Todos':
        queryset = queryset.filter(municipio=municipio_filtro)

    if assentamento_filtro != 'Todos':
        queryset = queryset.filter(assentamento=assentamento_filtro)

    if tipo_laudo_filtro != 'Todos':
        queryset = queryset.filter(tipo_laudo=tipo_laudo_filtro)

    if modalidade_filtro != 'Todos':
        queryset = queryset.filter(modalidade=modalidade_filtro)

    # Obter listas para filtros
    tecnicos = ['Todos'] + list(Laudo.objects.exclude(tecnico='').values_list('tecnico', flat=True).distinct())
    municipios = ['Todos'] + list(Laudo.objects.exclude(municipio='').values_list('municipio', flat=True).distinct())
    assentamentos = ['Todos'] + list(Laudo.objects.exclude(assentamento='').values_list('assentamento', flat=True).distinct())
    tipos_de_laudo = ['Todos'] + list(Laudo.objects.exclude(tipo_laudo='').values_list('tipo_laudo', flat=True).distinct())
    modalidades = ['Todos'] + list(Laudo.objects.exclude(modalidade='').values_list('modalidade', flat=True).distinct())

    # Calcular estatísticas para modalidades
    vistoria_count = Laudo.objects.filter(modalidade__icontains='VISTORIA').count()
    mutirao_count = Laudo.objects.filter(modalidade__icontains='MUTIR').count()

    # Meta total para cada modalidade (valores fixos)
    meta_vistoria = 4739
    meta_mutirao = 2746

    # Calcular percentuais
    percentual_vistoria = min((vistoria_count / meta_vistoria) * 100 if meta_vistoria > 0 else 0, 100)
    percentual_mutirao = min((mutirao_count / meta_mutirao) * 100 if meta_mutirao > 0 else 0, 100)

    # Gráfico de pizza - Distribuição por município
    municipio_chart = None
    municipio_counts = queryset.values('municipio').annotate(count=Count('id')).order_by('-count')

    if municipio_counts:
        df_municipios = pd.DataFrame(list(municipio_counts))

        # Limitar a 15 municípios mais frequentes
        if len(df_municipios) > 15:
            top_municipios = df_municipios.head(15)
            outros_count = df_municipios.iloc[15:]['count'].sum()
            outros_df = pd.DataFrame([{'municipio': 'Outros', 'count': outros_count}])
            df_municipios = pd.concat([top_municipios, outros_df], ignore_index=True)

        fig_municipio = px.pie(
            df_municipios,
            names='municipio',
            values='count',
            title='Distribuição dos Laudos por Município',
            hole=0.3
        )
        fig_municipio.update_traces(textposition='inside', textinfo='percent+label')
        municipio_chart = fig_municipio.to_json()

    # Gráfico de barras - Distribuição por tipo de laudo
    tipo_laudo_chart = None
    tipo_laudo_counts = queryset.values('tipo_laudo').annotate(count=Count('id')).order_by('-count')

    if tipo_laudo_counts:
        df_tipos = pd.DataFrame(list(tipo_laudo_counts))

        # Limitar a 10 tipos mais frequentes
        if len(df_tipos) > 10:
            top_tipos = df_tipos.head(10)
            outros_count = df_tipos.iloc[10:]['count'].sum()
            outros_df = pd.DataFrame([{'tipo_laudo': 'Outros', 'count': outros_count}])
            df_tipos = pd.concat([top_tipos, outros_df], ignore_index=True)

        fig_tipo = px.bar(
            df_tipos,
            x='tipo_laudo',
            y='count',
            title='Quantidade de Laudos por Tipo',
            labels={'tipo_laudo': 'Tipo de Laudo', 'count': 'Quantidade'}
        )
        fig_tipo.update_layout(xaxis_tickangle=-45)
        tipo_laudo_chart = fig_tipo.to_json()

    # Gráfico de barras - Distribuição por técnico
    tecnico_chart = None
    tecnico_counts = queryset.values('tecnico').annotate(count=Count('id')).order_by('-count')

    if tecnico_counts:
        df_tecnicos = pd.DataFrame(list(tecnico_counts))

        # Limitar a 10 técnicos mais frequentes
        if len(df_tecnicos) > 10:
            df_tecnicos = df_tecnicos.head(10)

        fig_tecnico = px.bar(
            df_tecnicos,
            x='tecnico',
            y='count',
            title='Quantidade de Laudos por Técnico',
            labels={'tecnico': 'Técnico', 'count': 'Quantidade'}
        )
        fig_tecnico.update_layout(xaxis_tickangle=-45)
        tecnico_chart = fig_tecnico.to_json()

    # Gráfico de barras - Distribuição por modalidade
    modalidade_chart = None
    modalidade_counts = queryset.values('modalidade').annotate(count=Count('id')).order_by('-count')

    if modalidade_counts:
        df_modalidades = pd.DataFrame(list(modalidade_counts))

        # Limitar a 10 modalidades mais frequentes
        if len(df_modalidades) > 10:
            df_modalidades = df_modalidades.head(10)

        fig_modalidade = px.bar(
            df_modalidades,
            x='modalidade',
            y='count',
            title='Quantidade de Laudos por Modalidade',
            labels={'modalidade': 'Modalidade', 'count': 'Quantidade'}
        )
        fig_modalidade.update_layout(xaxis_tickangle=-45)
        modalidade_chart = fig_modalidade.to_json()

    # Gráfico de barras - Laudos por mês/ano
    mensal_chart = None

    # Obter anos únicos dos laudos
    anos = Laudo.objects.dates('data_emissao', 'year')
    anos = [d.year for d in anos]

    if anos:
        # Criar DataFrame para dados mensais
        dados_mensais = []

        for ano in anos:
            for mes in range(1, 13):
                count = queryset.filter(data_emissao__year=ano, data_emissao__month=mes).count()
                dados_mensais.append({
                    'ano': ano,
                    'mes': mes,
                    'count': count
                })

        df_mensal = pd.DataFrame(dados_mensais)

        # Criar nomes dos meses
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        # Criar gráfico
        fig_mensal = go.Figure()

        for ano in anos:
            df_ano = df_mensal[df_mensal['ano'] == ano]
            fig_mensal.add_trace(go.Bar(
                x=meses_nomes,
                y=df_ano['count'],
                name=str(ano)
            ))

        fig_mensal.update_layout(
            title='Quantidade de Laudos por Mês/Ano',
            xaxis_title='Mês',
            yaxis_title='Quantidade',
            barmode='group'
        )

        mensal_chart = fig_mensal.to_json()

    # Gráficos de progresso para metas
    progresso_vistoria_chart = None
    progresso_mutirao_chart = None

    # Gráfico de progresso para vistorias
    fig_vistoria = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=vistoria_count,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Vistorias Realizadas"},
        delta={'reference': meta_vistoria, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, meta_vistoria], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, meta_vistoria/3], 'color': 'red'},
                {'range': [meta_vistoria/3, 2*meta_vistoria/3], 'color': 'orange'},
                {'range': [2*meta_vistoria/3, meta_vistoria], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': meta_vistoria
            }
        }
    ))
    fig_vistoria.update_layout(
        title="Progresso de Vistorias",
        height=300
    )
    progresso_vistoria_chart = fig_vistoria.to_json()

    # Gráfico de progresso para mutirões
    fig_mutirao = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=mutirao_count,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Mutirões Realizados"},
        delta={'reference': meta_mutirao, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, meta_mutirao], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, meta_mutirao/3], 'color': 'red'},
                {'range': [meta_mutirao/3, 2*meta_mutirao/3], 'color': 'orange'},
                {'range': [2*meta_mutirao/3, meta_mutirao], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': meta_mutirao
            }
        }
    ))
    fig_mutirao.update_layout(
        title="Progresso de Mutirões",
        height=300
    )
    progresso_mutirao_chart = fig_mutirao.to_json()

    # Converter queryset para lista para o template (limitado a 100 para não sobrecarregar)
    laudos_list = list(queryset.values('municipio', 'tipo_laudo', 'data_emissao', 'tecnico', 
                                       'modalidade', 'assentamento', 'lote', 'codigo_sipra')
                       .order_by('-data_emissao')[:100])

    # Preparar contexto para o template
    context = {
        'title': 'Dashboard de Laudos',
        'total_laudos': queryset.count(),
        'vistoria_count': vistoria_count,
        'mutirao_count': mutirao_count,
        'meta_vistoria': meta_vistoria,
        'meta_mutirao': meta_mutirao,
        'percentual_vistoria': percentual_vistoria,
        'percentual_mutirao': percentual_mutirao,
        'laudos': laudos_list,
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
        'tipo_laudo_chart': tipo_laudo_chart,
        'tecnico_chart': tecnico_chart,
        'modalidade_chart': modalidade_chart,
        'mensal_chart': mensal_chart,
        'progresso_vistoria_chart': progresso_vistoria_chart,
        'progresso_mutirao_chart': progresso_mutirao_chart,
    }

    return render(request, 'supervisao_ocupacional/laudos.html', context)

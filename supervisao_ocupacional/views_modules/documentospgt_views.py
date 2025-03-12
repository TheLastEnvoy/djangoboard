import json
from django.shortcuts import render
from django.db.models import Count, Q
from supervisao_ocupacional.models import DocumentoPGT
import plotly.graph_objects as go
import plotly.express as px
import plotly.utils

def documentospgt(request):
    # Obter todos os documentos PGT
    documentospgt = DocumentoPGT.objects.all()
    total_documentospgt = documentospgt.count()

    # Obter valores únicos para filtros
    tipos_documentopgt = ['Todos'] + list(documentospgt.values_list('tipo_documentopgt', flat=True).distinct())
    assentamentos = ['Todos'] + list(documentospgt.values_list('assentamento', flat=True).distinct())
    municipios = ['Todos'] + list(documentospgt.values_list('municipio', flat=True).distinct())
    nomes_t1 = ['Todos'] + list(documentospgt.values_list('nome_t1', flat=True).distinct())
    objetivos = ['Todos'] + list(documentospgt.values_list('objetivo', flat=True).distinct())

    # Obter parâmetros de filtro
    tipo_documentopgt_filtro = request.GET.get('tipo_documentopgt', 'Todos')
    assentamento_filtro = request.GET.get('assentamento', 'Todos')
    municipio_filtro = request.GET.get('municipio', 'Todos')
    nome_t1_filtro = request.GET.get('nome_t1', 'Todos')
    objetivo_filtro = request.GET.get('objetivo', 'Todos')

    # Aplicar filtros
    documentospgt_filtrados = documentospgt

    if tipo_documentopgt_filtro != 'Todos':
        documentospgt_filtrados = documentospgt_filtrados.filter(tipo_documentopgt=tipo_documentopgt_filtro)

    if assentamento_filtro != 'Todos':
        documentospgt_filtrados = documentospgt_filtrados.filter(assentamento=assentamento_filtro)

    if municipio_filtro != 'Todos':
        documentospgt_filtrados = documentospgt_filtrados.filter(municipio=municipio_filtro)

    if nome_t1_filtro != 'Todos':
        documentospgt_filtrados = documentospgt_filtrados.filter(nome_t1=nome_t1_filtro)

    if objetivo_filtro != 'Todos':
        documentospgt_filtrados = documentospgt_filtrados.filter(objetivo=objetivo_filtro)

    # Obter contagens para as barras de progresso
    # 2.2.1. Relatório de conformidades para regularização
    total_relatorios_conf = 2246  # Meta total
    relatorios_conf_atual = DocumentoPGT.objects.filter(
        tipo_documentopgt='Relatório de conformidades para regularização'
    ).count()
    percentual_relatorios_conf = (relatorios_conf_atual / total_relatorios_conf) * 100 if total_relatorios_conf > 0 else 0

    # 2.2.2. Solicitação de documentação complementar
    total_solicitacoes = 674  # Meta total
    solicitacoes_atual = DocumentoPGT.objects.filter(
        tipo_documentopgt='Solicitação de documentação complementar'
    ).count()
    percentual_solicitacoes = (solicitacoes_atual / total_solicitacoes) * 100 if total_solicitacoes > 0 else 0

    # 2.2.3. Segundos relatórios de conformidades para regularização
    total_segundos_relatorios = 337  # Meta total
    segundos_relatorios_atual = DocumentoPGT.objects.filter(
        tipo_documentopgt='Relatório de conformidades para regularização (2º Relatório)'
    ).count()
    percentual_segundos_relatorios = (segundos_relatorios_atual / total_segundos_relatorios) * 100 if total_segundos_relatorios > 0 else 0

    # 2.2.4. Análise para regularização
    total_analise_reg = 1622  # Meta total
    analise_reg_atual = DocumentoPGT.objects.filter(
        tipo_documentopgt='Análise para regularização'
    ).count()
    percentual_analise_reg = (analise_reg_atual / total_analise_reg) * 100 if total_analise_reg > 0 else 0

    # Adicionar contagem para Relatório de conformidades para titulação
    titulacao_atual = DocumentoPGT.objects.filter(
        tipo_documentopgt='Relatório de conformidades para titulação'
    ).count()

    # Calcular o percentual de titulação (meta: 200)
    percentual_titulacao = (titulacao_atual / 200) * 100 if titulacao_atual > 0 else 0

    # Gerar dados para gráficos
    # Gráfico de tipo de documento
    tipo_documentopgt_counts = documentospgt_filtrados.values('tipo_documentopgt').annotate(count=Count('id')).order_by('-count')
    tipo_documentopgt_fig = px.pie(
        tipo_documentopgt_counts, 
        values='count', 
        names='tipo_documentopgt', 
        title='Distribuição por Tipo de Documento',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    tipo_documentopgt_fig.update_layout(margin=dict(t=50, b=0, l=0, r=0))
    # Usar plotly.utils.PlotlyJSONEncoder para serializar o gráfico
    tipo_documentopgt_chart = json.dumps(tipo_documentopgt_fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)

    # Gráfico de município
    municipio_counts = documentospgt_filtrados.values('municipio').annotate(count=Count('id')).order_by('-count')
    municipio_fig = px.bar(
        municipio_counts, 
        x='municipio', 
        y='count', 
        title='Distribuição por Município',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    municipio_fig.update_layout(margin=dict(t=50, b=100, l=50, r=0), xaxis_tickangle=-45)
    municipio_chart = json.dumps(municipio_fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)

    # Gráfico de assentamento
    assentamento_counts = documentospgt_filtrados.values('assentamento').annotate(count=Count('id')).order_by('-count')
    assentamento_fig = px.bar(
        assentamento_counts, 
        x='assentamento', 
        y='count', 
        title='Distribuição por Assentamento',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    assentamento_fig.update_layout(margin=dict(t=50, b=100, l=50, r=0), xaxis_tickangle=-45)
    assentamento_chart = json.dumps(assentamento_fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)

    # Gráfico de objetivo (se houver mais de um objetivo)
    objetivo_chart = None
    if len(objetivos) > 1:
        objetivo_counts = documentospgt_filtrados.values('objetivo').annotate(count=Count('id')).order_by('-count')
        objetivo_fig = px.pie(
            objetivo_counts, 
            values='count', 
            names='objetivo', 
            title='Distribuição por Objetivo',
            color_discrete_sequence=px.colors.qualitative.Pastel1
        )
        objetivo_fig.update_layout(margin=dict(t=50, b=0, l=0, r=0))
        objetivo_chart = json.dumps(objetivo_fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)

    # Dados para tabela de tipo de documento por assentamento
    tipo_assentamento_list = list(documentospgt_filtrados.values('tipo_documentopgt', 'assentamento')
                                  .annotate(count=Count('id'))
                                  .order_by('-count'))

    # Converter para formato adequado para o template
    for item in tipo_assentamento_list:
        item['Tipo_de_documento PGT'] = item.pop('tipo_documentopgt')
        item['Assentamento'] = item.pop('assentamento')
        item['Quantidade'] = item.pop('count')

    # Preparar dados para a tabela completa
    documentospgt_list = []
    for doc in documentospgt_filtrados:
        doc_dict = {
            'Tipo_de_documento PGT': doc.tipo_documentopgt,
            'Município': doc.municipio,
            'Assentamento': doc.assentamento,
            'Nome_T1': doc.nome_t1,
            'Objetivo': doc.objetivo,
            'Código_SIPRA': doc.codigo_sipra,
            'Autenticador': doc.autenticador,
            'Segundo_Relatório': 'Sim' if doc.segundo_relatorio else 'Não',
            'Data': doc.data_criacao.strftime('%d/%m/%Y') if doc.data_criacao else '-'
        }
        documentospgt_list.append(doc_dict)

    # Preparar contexto para o template
    context = {
        'title': 'Dashboard de Documentos (PGT)',
        'documentospgt': documentospgt_list,
        'total_documentospgt': total_documentospgt,
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
        'tipo_documentopgt_chart': tipo_documentopgt_chart,
        'municipio_chart': municipio_chart,
        'assentamento_chart': assentamento_chart,
        'objetivo_chart': objetivo_chart if len(objetivos) > 1 else None,
        'tipo_assentamento_list': tipo_assentamento_list,

        # Contagens e percentuais para barras de progresso
        'total_relatorios_conf': total_relatorios_conf,
        'relatorios_conf_atual': relatorios_conf_atual,
        'percentual_relatorios_conf': percentual_relatorios_conf,

        'total_solicitacoes': total_solicitacoes,
        'solicitacoes_atual': solicitacoes_atual,
        'percentual_solicitacoes': percentual_solicitacoes,

        'total_segundos_relatorios': total_segundos_relatorios,
        'segundos_relatorios_atual': segundos_relatorios_atual,
        'percentual_segundos_relatorios': percentual_segundos_relatorios,

        'total_analise_reg': total_analise_reg,
        'analise_reg_atual': analise_reg_atual,
        'percentual_analise_reg': percentual_analise_reg,

        # Adicionar titulação ao contexto com o percentual calculado
        'titulacao_atual': titulacao_atual,
        'percentual_titulacao': percentual_titulacao,
    }

    # Verificar se há erro
    if total_documentospgt == 0:
        context['error_message'] = 'Não foram encontrados documentos PGT no banco de dados.'

    return render(request, 'supervisao_ocupacional/documentospgt.html', context)

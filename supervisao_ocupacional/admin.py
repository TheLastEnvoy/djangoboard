# supervisao_ocupacional/admin.py
from django.contrib import admin
from .models import Laudo, DocumentoPGT, DocumentoRecebido, Parecer, Planilha

class LaudoAdmin(admin.ModelAdmin):
    list_display = ('tipo_laudo', 'municipio', 'data_emissao', 'tecnico', 'assentamento')
    list_filter = ('tipo_laudo', 'municipio', 'data_emissao', 'tecnico')
    search_fields = ('tipo_laudo', 'municipio', 'tecnico', 'assentamento')
    date_hierarchy = 'data_emissao'

class DocumentoPGTAdmin(admin.ModelAdmin):
    # Atualizado de 'tipo_documento' para 'tipo_documentopgt'
    list_display = ('tipo_documentopgt', 'municipio', 'assentamento', 'nome_t1', 'data_criacao')
    # Atualizado de 'tipo_documento' para 'tipo_documentopgt'
    list_filter = ('tipo_documentopgt', 'municipio', 'assentamento', 'data_criacao')
    search_fields = ('tipo_documentopgt', 'municipio', 'assentamento', 'nome_t1')
    date_hierarchy = 'data_criacao'

class DocumentoRecebidoAdmin(admin.ModelAdmin):
    list_display = ('tipo_documento', 'municipio', 'data_recebimento', 'status')
    list_filter = ('tipo_documento', 'municipio', 'data_recebimento', 'status')
    search_fields = ('tipo_documento', 'municipio', 'observacoes')
    date_hierarchy = 'data_recebimento'

class ParecerAdmin(admin.ModelAdmin):
    list_display = ('tipo_parecer', 'municipio', 'data_emissao')
    list_filter = ('tipo_parecer', 'municipio', 'data_emissao')
    search_fields = ('tipo_parecer', 'municipio')
    date_hierarchy = 'data_emissao'

class PlanilhaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'data_criacao')
    list_filter = ('tipo', 'data_criacao')
    search_fields = ('nome', 'tipo')
    date_hierarchy = 'data_criacao'

admin.site.register(Laudo, LaudoAdmin)
admin.site.register(DocumentoPGT, DocumentoPGTAdmin)
admin.site.register(DocumentoRecebido, DocumentoRecebidoAdmin)
admin.site.register(Parecer, ParecerAdmin)
admin.site.register(Planilha, PlanilhaAdmin)

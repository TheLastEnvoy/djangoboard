import os
import pandas as pd
from django.core.management.base import BaseCommand
from supervisao_ocupacional.models import DocumentoPGT
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
    help = 'Importa documentos PGT de uma planilha Excel'

    def add_arguments(self, parser):
        parser.add_argument('arquivo_excel', type=str, help='Caminho para o arquivo Excel')

    def handle(self, *args, **options):
        arquivo_excel = options['arquivo_excel']

        # Verificar se o arquivo existe
        if not os.path.exists(arquivo_excel):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {arquivo_excel}'))
            self.stdout.write(self.style.WARNING(f'Diretório atual: {os.getcwd()}'))
            return

        try:
            # Carregar dados da planilha
            self.stdout.write(self.style.SUCCESS(f'Carregando dados de: {arquivo_excel}'))
            df = pd.read_excel(arquivo_excel)

            # Mostrar informações sobre os dados
            self.stdout.write(self.style.SUCCESS(f'Total de linhas na planilha: {len(df)}'))
            self.stdout.write(self.style.SUCCESS(f'Colunas disponíveis: {", ".join(df.columns)}'))

            # Verificar se as colunas necessárias existem
            colunas_necessarias = [
                'Tipo de documento PGT', 'Assentamento', 'Município', 
                'Código SIPRA', 'Nome T1', 'Autenticador', 'Objetivo'
            ]

            for coluna in colunas_necessarias:
                if coluna not in df.columns:
                    self.stdout.write(self.style.ERROR(f'Coluna {coluna} não encontrada na planilha'))
                    return

            # Limpar dados existentes (opcional)
            if DocumentoPGT.objects.exists():
                resposta = input('Deseja limpar os documentos existentes antes de importar? (s/n): ')
                if resposta.lower() == 's':
                    count = DocumentoPGT.objects.count()
                    DocumentoPGT.objects.all().delete()
                    self.stdout.write(self.style.WARNING(f'Removidos {count} documentos existentes'))

            # Contador para acompanhar o progresso
            contador = 0

            # Iterar sobre as linhas do DataFrame
            for index, row in df.iterrows():
                # Criar novo documento
                doc = DocumentoPGT(
                    tipo_documentopgt=row['Tipo de documento PGT'],
                    assentamento=row['Assentamento'],
                    municipio=row['Município'],
                    codigo_sipra=str(row['Código SIPRA']) if not pd.isna(row['Código SIPRA']) else '',
                    nome_t1=row['Nome T1'] if not pd.isna(row['Nome T1']) else '',
                    autenticador=row['Autenticador'] if not pd.isna(row['Autenticador']) else '',
                    objetivo=row['Objetivo'] if not pd.isna(row['Objetivo']) else '',
                    segundo_relatorio=True if 'Segundo Relatório' in df.columns and row['Segundo Relatório'] == 'Sim' else False,
                    data_criacao=timezone.now()  # Usar data atual como padrão
                )
                doc.save()
                contador += 1

                # Mostrar progresso
                if contador % 50 == 0:
                    self.stdout.write(self.style.SUCCESS(f"Importados {contador} documentos..."))

            self.stdout.write(self.style.SUCCESS(f"Importação concluída. Total de {contador} documentos importados."))

            # Verificar contagem por tipo
            self.stdout.write(self.style.SUCCESS("Contagem por tipo de documento:"))
            for tipo in DocumentoPGT.objects.values_list('tipo_documentopgt', flat=True).distinct():
                count = DocumentoPGT.objects.filter(tipo_documentopgt=tipo).count()
                self.stdout.write(f"- '{tipo}': {count} documentos")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro durante a importação: {str(e)}'))

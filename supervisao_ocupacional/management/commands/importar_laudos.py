# supervisao_ocupacional/management/commands/importar_laudos.py
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from supervisao_ocupacional.models import Laudo
from django.utils.dateparse import parse_date
import traceback
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa dados da planilha de laudos para o banco de dados'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando importação de laudos...')

        # Caminho para o arquivo
        file_path = os.path.join(settings.BASE_DIR, 'supervisao_ocupacional', 'data', '01_laudos_SO_infos.xlsx')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {file_path}'))
            return

        # Limpar registros existentes
        Laudo.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            sample_data = df.head(3).to_dict('records')
            for i, row in enumerate(sample_data):
                self.stdout.write(f"Linha {i+1}: {row}")

            # Verificar se há dados na planilha
            if df.empty:
                self.stdout.write(self.style.ERROR('A planilha está vazia!'))
                return

            # Tentar identificar as colunas corretas
            self.stdout.write("Todas as colunas disponíveis:")
            for col in df.columns:
                self.stdout.write(f"- {col}")

            # Tentar importar de forma simples primeiro
            count = 0
            for _, row in df.iterrows():
                try:
                    # Extrair valores diretamente das colunas
                    municipio = str(row.get('Município', '')) if pd.notna(row.get('Município', '')) else 'Desconhecido'
                    tipo_laudo = str(row.get('Tipo de Laudo', '')) if pd.notna(row.get('Tipo de Laudo', '')) else 'Não especificado'

                    # MODIFICAÇÃO PRINCIPAL: Tratamento melhorado para a data
                    data_raw = row.get('Data', None)
                    data_emissao = None

                    if pd.notna(data_raw):
                        try:
                            # Se for uma string, tenta analisar
                            if isinstance(data_raw, str):
                                # Tenta vários formatos de data comuns no Brasil
                                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']:
                                    try:
                                        data_emissao = datetime.strptime(data_raw, fmt).date()
                                        break
                                    except ValueError:
                                        continue

                                # Se ainda não conseguiu, tenta o parse genérico
                                if data_emissao is None:
                                    data_emissao = parse_date(data_raw)

                            # Se for um objeto datetime ou timestamp do pandas
                            elif hasattr(data_raw, 'date'):
                                data_emissao = data_raw.date()

                            # Se for um número (possivelmente um timestamp)
                            elif isinstance(data_raw, (int, float)):
                                try:
                                    # Tenta converter de timestamp para data
                                    data_emissao = datetime.fromtimestamp(data_raw).date()
                                except:
                                    pass
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Erro ao processar data "{data_raw}": {str(e)}'))
                            data_emissao = None

                    # IMPORTANTE: Não definimos mais uma data padrão se não conseguirmos extrair
                    # Se não conseguir extrair a data, deixa como None para identificar problemas

                    # Extrair outros campos
                    tecnico = str(row.get('Técnico', '')) if pd.notna(row.get('Técnico', '')) else ''
                    modalidade = str(row.get('Modalidade', '')) if pd.notna(row.get('Modalidade', '')) else ''
                    assentamento = str(row.get('Assentamento', '')) if pd.notna(row.get('Assentamento', '')) else ''
                    lote = str(row.get('Lote', '')) if pd.notna(row.get('Lote', '')) else ''
                    arquivo = str(row.get('Arquivo', '')) if pd.notna(row.get('Arquivo', '')) else ''
                    codigo_sipra = str(row.get('Código SIPRA', '')) if pd.notna(row.get('Código SIPRA', '')) else ''

                    # Criar o objeto Laudo
                    laudo = Laudo(
                        municipio=municipio,
                        tipo_laudo=tipo_laudo,
                        data_emissao=data_emissao,  # Pode ser None se não conseguirmos extrair
                        tecnico=tecnico,
                        modalidade=modalidade,
                        assentamento=assentamento,
                        lote=lote,
                        arquivo=arquivo,
                        codigo_sipra=codigo_sipra
                    )
                    laudo.save()
                    count += 1

                    # Log a cada 100 registros
                    if count % 100 == 0:
                        self.stdout.write(f'Importados {count} laudos...')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao importar linha: {str(e)}'))
                    self.stdout.write(self.style.ERROR(f'Dados da linha: {row.to_dict()}'))

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} laudos importados.'))

            # Verificar laudos sem data
            laudos_sem_data = Laudo.objects.filter(data_emissao__isnull=True).count()
            if laudos_sem_data > 0:
                self.stdout.write(self.style.WARNING(f'Atenção: {laudos_sem_data} laudos foram importados sem data de emissão.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

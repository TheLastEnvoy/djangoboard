# supervisao_ocupacional/management/commands/importar_dados.py
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from supervisao_ocupacional.models import DocumentoPGT, DocumentoRecebido, Laudo, Parecer, Planilha
from django.utils.dateparse import parse_date
import traceback
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa dados das planilhas Excel para o banco de dados'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando importação de planilhas...')

        # Caminho para o diretório de dados dentro da aplicação
        data_dir = os.path.join(settings.BASE_DIR, 'supervisao_ocupacional', 'data')

        # Verificar se o diretório existe
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Diretório não encontrado: {data_dir}'))
            return

        # Mostrar o caminho completo para depuração
        self.stdout.write(f'Diretório de dados: {data_dir}')

        # Listar arquivos no diretório
        try:
            files = os.listdir(data_dir)
            self.stdout.write(f'Arquivos encontrados: {files}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao listar arquivos: {str(e)}'))

        # Importar Laudos
        try:
            laudos_file = os.path.join(data_dir, '01_laudos_SO_infos.xlsx')
            if os.path.exists(laudos_file):
                self.stdout.write(f'Arquivo encontrado: {laudos_file}')
                self.importar_laudos(laudos_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {laudos_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar laudos: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar DocumentosPGT
        try:
            pgt_file = os.path.join(data_dir, '02_contPGT.xlsx')
            if os.path.exists(pgt_file):
                self.stdout.write(f'Arquivo encontrado: {pgt_file}')
                self.importar_documentos_pgt(pgt_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {pgt_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar documentos PGT: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar DocumentosRecebidos
        try:
            docs_file = os.path.join(data_dir, '03_contDocsRecebidos.xlsx')
            if os.path.exists(docs_file):
                self.stdout.write(f'Arquivo encontrado: {docs_file}')
                self.importar_documentos_recebidos(docs_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {docs_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar documentos recebidos: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar Pareceres
        try:
            pareceres_file = os.path.join(data_dir, '04_contPareceres.xlsx')
            if os.path.exists(pareceres_file):
                self.stdout.write(f'Arquivo encontrado: {pareceres_file}')
                self.importar_pareceres(pareceres_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {pareceres_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar pareceres: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar Planilhas
        try:
            planilhas_file = os.path.join(data_dir, '05_contPlanilhas.xlsx')
            if os.path.exists(planilhas_file):
                self.stdout.write(f'Arquivo encontrado: {planilhas_file}')
                self.importar_planilhas(planilhas_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {planilhas_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar planilhas: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))

    def importar_laudos(self, file_path):
        self.stdout.write(f'Importando laudos de {file_path}...')

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

            # Listar todas as colunas disponíveis
            self.stdout.write("Todas as colunas disponíveis:")
            for col in df.columns:
                self.stdout.write(f"- {col}")

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                try:
                    # Extrair valores diretamente das colunas
                    municipio = str(row.get('Município', '')) if pd.notna(row.get('Município', '')) else 'Desconhecido'
                    tipo_laudo = str(row.get('Tipo de Laudo', '')) if pd.notna(row.get('Tipo de Laudo', '')) else 'Não especificado'

                    # Tratamento melhorado para a data
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

# supervisao_ocupacional/management/commands/importar_dados.py
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from supervisao_ocupacional.models import DocumentoPGT, DocumentoRecebido, Laudo, Parecer, Planilha
from django.utils.dateparse import parse_date
import traceback
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa dados das planilhas Excel para o banco de dados'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando importação de planilhas...')

        # Caminho para o diretório de dados dentro da aplicação
        data_dir = os.path.join(settings.BASE_DIR, 'supervisao_ocupacional', 'data')

        # Verificar se o diretório existe
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Diretório não encontrado: {data_dir}'))
            return

        # Mostrar o caminho completo para depuração
        self.stdout.write(f'Diretório de dados: {data_dir}')

        # Listar arquivos no diretório
        try:
            files = os.listdir(data_dir)
            self.stdout.write(f'Arquivos encontrados: {files}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao listar arquivos: {str(e)}'))

        # Importar Laudos
        try:
            laudos_file = os.path.join(data_dir, '01_laudos_SO_infos.xlsx')
            if os.path.exists(laudos_file):
                self.stdout.write(f'Arquivo encontrado: {laudos_file}')
                self.importar_laudos(laudos_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {laudos_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar laudos: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar DocumentosPGT
        try:
            pgt_file = os.path.join(data_dir, '02_contPGT.xlsx')
            if os.path.exists(pgt_file):
                self.stdout.write(f'Arquivo encontrado: {pgt_file}')
                self.importar_documentos_pgt(pgt_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {pgt_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar documentos PGT: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar DocumentosRecebidos
        try:
            docs_file = os.path.join(data_dir, '03_contDocsRecebidos.xlsx')
            if os.path.exists(docs_file):
                self.stdout.write(f'Arquivo encontrado: {docs_file}')
                self.importar_documentos_recebidos(docs_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {docs_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar documentos recebidos: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar Pareceres
        try:
            pareceres_file = os.path.join(data_dir, '04_contPareceres.xlsx')
            if os.path.exists(pareceres_file):
                self.stdout.write(f'Arquivo encontrado: {pareceres_file}')
                self.importar_pareceres(pareceres_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {pareceres_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar pareceres: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Importar Planilhas
        try:
            planilhas_file = os.path.join(data_dir, '05_contPlanilhas.xlsx')
            if os.path.exists(planilhas_file):
                self.stdout.write(f'Arquivo encontrado: {planilhas_file}')
                self.importar_planilhas(planilhas_file)
            else:
                self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {planilhas_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar planilhas: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))

    def importar_laudos(self, file_path):
        self.stdout.write(f'Importando laudos de {file_path}...')

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

            # Listar todas as colunas disponíveis
            self.stdout.write("Todas as colunas disponíveis:")
            for col in df.columns:
                self.stdout.write(f"- {col}")

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                try:
                    # Extrair valores diretamente das colunas
                    municipio = str(row.get('Município', '')) if pd.notna(row.get('Município', '')) else 'Desconhecido'
                    tipo_laudo = str(row.get('Tipo de Laudo', '')) if pd.notna(row.get('Tipo de Laudo', '')) else 'Não especificado'

                    # Tratamento melhorado para a data
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

    def importar_documentos_pgt(self, file_path):
        # O código original permanece inalterado
        self.stdout.write(f'Importando documentos PGT de {file_path}...')

        # Limpar registros existentes
        DocumentoPGT.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            self.stdout.write(str(df.head().to_dict('records')))

            # Mapear colunas da planilha para campos do modelo
            column_mapping = {
                'Tipo': 'tipo_documento',
                'Município': 'municipio',
                'Assentamento': 'assentamento',
                'Nome': 'nome_t1',
                'Objetivo': 'objetivo',
                'Data': 'data_criacao'
            }

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                doc_data = {}

                # Mapear campos
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)

                        # Tratar valores NaN
                        if pd.isna(value):
                            if model_field == 'data_criacao':
                                value = timezone.now().date()
                            elif model_field == 'municipio':
                                value = 'Desconhecido'
                            elif model_field == 'tipo_documento':
                                value = 'Não especificado'
                            else:
                                value = ''

                        # Converter data
                        if model_field == 'data_criacao' and value is not None:
                            try:
                                if isinstance(value, str):
                                    value = parse_date(value)
                                elif hasattr(value, 'date'):
                                    value = value.date()
                            except:
                                value = timezone.now().date()

                        doc_data[model_field] = value

                # Garantir que campos obrigatórios estejam presentes
                if 'municipio' not in doc_data:
                    doc_data['municipio'] = 'Desconhecido'
                if 'tipo_documento' not in doc_data:
                    doc_data['tipo_documento'] = 'Não especificado'
                if 'data_criacao' not in doc_data:
                    doc_data['data_criacao'] = timezone.now().date()

                # Criar o objeto DocumentoPGT
                DocumentoPGT.objects.create(**doc_data)
                count += 1

                # Log a cada 100 registros
                if count % 100 == 0:
                    self.stdout.write(f'Importados {count} documentos PGT...')

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} documentos PGT importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def importar_documentos_recebidos(self, file_path):
        # O código original permanece inalterado
        self.stdout.write(f'Importando documentos recebidos de {file_path}...')

        # Limpar registros existentes
        DocumentoRecebido.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            self.stdout.write(str(df.head().to_dict('records')))

            # Mapear colunas da planilha para campos do modelo
            column_mapping = {
                'Tipo': 'tipo_documento',
                'Município': 'municipio',
                'Data': 'data_recebimento',
                'Status': 'status',
                'Observações': 'observacoes'
            }

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                doc_data = {}

                # Mapear campos
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)

                        # Tratar valores NaN
                        if pd.isna(value):
                            if model_field == 'data_recebimento':
                                value = timezone.now().date()
                            elif model_field == 'municipio':
                                value = 'Desconhecido'
                            elif model_field == 'tipo_documento':
                                value = 'Não especificado'
                            elif model_field == 'status':
                                value = 'Recebido'
                            else:
                                value = ''

                        # Converter data
                        if model_field == 'data_recebimento' and value is not None:
                            try:
                                if isinstance(value, str):
                                    value = parse_date(value)
                                elif hasattr(value, 'date'):
                                    value = value.date()
                            except:
                                value = timezone.now().date()

                        doc_data[model_field] = value

                # Garantir que campos obrigatórios estejam presentes
                if 'municipio' not in doc_data:
                    doc_data['municipio'] = 'Desconhecido'
                if 'tipo_documento' not in doc_data:
                    doc_data['tipo_documento'] = 'Não especificado'
                if 'data_recebimento' not in doc_data:
                    doc_data['data_recebimento'] = timezone.now().date()
                if 'status' not in doc_data:
                    doc_data['status'] = 'Recebido'

                # Criar o objeto DocumentoRecebido
                DocumentoRecebido.objects.create(**doc_data)
                count += 1

                # Log a cada 100 registros
                if count % 100 == 0:
                    self.stdout.write(f'Importados {count} documentos recebidos...')

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} documentos recebidos importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def importar_pareceres(self, file_path):
        # O código original permanece inalterado
        self.stdout.write(f'Importando pareceres de {file_path}...')

        # Limpar registros existentes
        Parecer.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            self.stdout.write(str(df.head().to_dict('records')))

            # Mapear colunas da planilha para campos do modelo
            column_mapping = {
                'Tipo': 'tipo_parecer',
                'Município': 'municipio',
                'Data': 'data_emissao'
            }

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                parecer_data = {}

                # Mapear campos
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)

                        # Tratar valores NaN
                        if pd.isna(value):
                            if model_field == 'data_emissao':
                                value = timezone.now().date()
                            elif model_field == 'municipio':
                                value = 'Desconhecido'
                            elif model_field == 'tipo_parecer':
                                value = 'Não especificado'
                            else:
                                value = ''

                        # Converter data
                        if model_field == 'data_emissao' and value is not None:
                            try:
                                if isinstance(value, str):
                                    value = parse_date(value)
                                elif hasattr(value, 'date'):
                                    value = value.date()
                            except:
                                value = timezone.now().date()

                        parecer_data[model_field] = value

                # Garantir que campos obrigatórios estejam presentes
                if 'municipio' not in parecer_data:
                    parecer_data['municipio'] = 'Desconhecido'
                if 'tipo_parecer' not in parecer_data:
                    parecer_data['tipo_parecer'] = 'Não especificado'
                if 'data_emissao' not in parecer_data:
                    parecer_data['data_emissao'] = timezone.now().date()

                # Criar o objeto Parecer
                Parecer.objects.create(**parecer_data)
                count += 1

                # Log a cada 100 registros
                if count % 100 == 0:
                    self.stdout.write(f'Importados {count} pareceres...')

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} pareceres importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def importar_planilhas(self, file_path):
        # O código original permanece inalterado
        self.stdout.write(f'Importando planilhas de {file_path}...')

        # Limpar registros existentes
        Planilha.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            self.stdout.write(str(df.head().to_dict('records')))

            # Mapear colunas da planilha para campos do modelo
            column_mapping = {
                'Nome': 'nome',
                'Tipo': 'tipo',
                'Data': 'data_criacao'
            }

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                planilha_data = {}

                # Mapear campos
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)

                        # Tratar valores NaN
                        if pd.isna(value):
                            if model_field == 'data_criacao':
                                value = timezone.now().date()
                            elif model_field == 'nome':
                                value = 'Sem nome'
                            elif model_field == 'tipo':
                                value = 'Não especificado'
                            else:
                                value = ''

                        # Converter data
                        if model_field == 'data_criacao' and value is not None:
                            try:
                                if isinstance(value, str):
                                    value = parse_date(value)
                                elif hasattr(value, 'date'):
                                    value = value.date()
                            except:
                                value = timezone.now().date()

                        planilha_data[model_field] = value

                # Garantir que campos obrigatórios estejam presentes
                if 'nome' not in planilha_data:
                    planilha_data['nome'] = 'Sem nome'
                if 'tipo' not in planilha_data:
                    planilha_data['tipo'] = 'Não especificado'
                if 'data_criacao' not in planilha_data:
                    planilha_data['data_criacao'] = timezone.now().date()

                # Criar o objeto Planilha
                Planilha.objects.create(**planilha_data)
                count += 1

                # Log a cada 100 registros
                if count % 100 == 0:
                    self.stdout.write(f'Importados {count} planilhas...')

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} planilhas importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def importar_documentos_recebidos(self, file_path):
        # O código original permanece inalterado
        self.stdout.write(f'Importando documentos recebidos de {file_path}...')

        # Limpar registros existentes
        DocumentoRecebido.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            self.stdout.write(str(df.head().to_dict('records')))

            # Mapear colunas da planilha para campos do modelo
            column_mapping = {
                'Tipo': 'tipo_documento',
                'Município': 'municipio',
                'Data': 'data_recebimento',
                'Status': 'status',
                'Observações': 'observacoes'
            }

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                doc_data = {}

                # Mapear campos
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)

                        # Tratar valores NaN
                        if pd.isna(value):
                            if model_field == 'data_recebimento':
                                value = timezone.now().date()
                            elif model_field == 'municipio':
                                value = 'Desconhecido'
                            elif model_field == 'tipo_documento':
                                value = 'Não especificado'
                            elif model_field == 'status':
                                value = 'Recebido'
                            else:
                                value = ''

                        # Converter data
                        if model_field == 'data_recebimento' and value is not None:
                            try:
                                if isinstance(value, str):
                                    value = parse_date(value)
                                elif hasattr(value, 'date'):
                                    value = value.date()
                            except:
                                value = timezone.now().date()

                        doc_data[model_field] = value

                # Garantir que campos obrigatórios estejam presentes
                if 'municipio' not in doc_data:
                    doc_data['municipio'] = 'Desconhecido'
                if 'tipo_documento' not in doc_data:
                    doc_data['tipo_documento'] = 'Não especificado'
                if 'data_recebimento' not in doc_data:
                    doc_data['data_recebimento'] = timezone.now().date()
                if 'status' not in doc_data:
                    doc_data['status'] = 'Recebido'

                # Criar o objeto DocumentoRecebido
                DocumentoRecebido.objects.create(**doc_data)
                count += 1

                # Log a cada 100 registros
                if count % 100 == 0:
                    self.stdout.write(f'Importados {count} documentos recebidos...')

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} documentos recebidos importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def importar_pareceres(self, file_path):
        # O código original permanece inalterado
        self.stdout.write(f'Importando pareceres de {file_path}...')

        # Limpar registros existentes
        Parecer.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            self.stdout.write(str(df.head().to_dict('records')))

            # Mapear colunas da planilha para campos do modelo
            column_mapping = {
                'Tipo': 'tipo_parecer',
                'Município': 'municipio',
                'Data': 'data_emissao'
            }

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                parecer_data = {}

                # Mapear campos
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)

                        # Tratar valores NaN
                        if pd.isna(value):
                            if model_field == 'data_emissao':
                                value = timezone.now().date()
                            elif model_field == 'municipio':
                                value = 'Desconhecido'
                            elif model_field == 'tipo_parecer':
                                value = 'Não especificado'
                            else:
                                value = ''

                        # Converter data
                        if model_field == 'data_emissao' and value is not None:
                            try:
                                if isinstance(value, str):
                                    value = parse_date(value)
                                elif hasattr(value, 'date'):
                                    value = value.date()
                            except:
                                value = timezone.now().date()

                        parecer_data[model_field] = value

                # Garantir que campos obrigatórios estejam presentes
                if 'municipio' not in parecer_data:
                    parecer_data['municipio'] = 'Desconhecido'
                if 'tipo_parecer' not in parecer_data:
                    parecer_data['tipo_parecer'] = 'Não especificado'
                if 'data_emissao' not in parecer_data:
                    parecer_data['data_emissao'] = timezone.now().date()

                # Criar o objeto Parecer
                Parecer.objects.create(**parecer_data)
                count += 1

                # Log a cada 100 registros
                if count % 100 == 0:
                    self.stdout.write(f'Importados {count} pareceres...')

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} pareceres importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def importar_planilhas(self, file_path):
        # O código original permanece inalterado
        self.stdout.write(f'Importando planilhas de {file_path}...')

        # Limpar registros existentes
        Planilha.objects.all().delete()

        # Ler planilha
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Colunas encontradas: {list(df.columns)}')

            # Mostrar as primeiras linhas da planilha para depuração
            self.stdout.write("Primeiras linhas da planilha:")
            self.stdout.write(str(df.head().to_dict('records')))

            # Mapear colunas da planilha para campos do modelo
            column_mapping = {
                'Nome': 'nome',
                'Tipo': 'tipo',
                'Data': 'data_criacao'
            }

            # Importar registros
            count = 0
            for _, row in df.iterrows():
                planilha_data = {}

                # Mapear campos
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row.get(excel_col)

                        # Tratar valores NaN
                        if pd.isna(value):
                            if model_field == 'data_criacao':
                                value = timezone.now().date()
                            elif model_field == 'nome':
                                value = 'Sem nome'
                            elif model_field == 'tipo':
                                value = 'Não especificado'
                            else:
                                value = ''

                        # Converter data
                        if model_field == 'data_criacao' and value is not None:
                            try:
                                if isinstance(value, str):
                                    value = parse_date(value)
                                elif hasattr(value, 'date'):
                                    value = value.date()
                            except:
                                value = timezone.now().date()

                        planilha_data[model_field] = value

                # Garantir que campos obrigatórios estejam presentes
                if 'nome' not in planilha_data:
                    planilha_data['nome'] = 'Sem nome'
                if 'tipo' not in planilha_data:
                    planilha_data['tipo'] = 'Não especificado'
                if 'data_criacao' not in planilha_data:
                    planilha_data['data_criacao'] = timezone.now().date()

                # Criar o objeto Planilha
                Planilha.objects.create(**planilha_data)
                count += 1

                # Log a cada 100 registros
                if count % 100 == 0:
                    self.stdout.write(f'Importados {count} planilhas...')

            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {count} planilhas importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar planilha: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

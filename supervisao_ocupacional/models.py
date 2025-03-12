from django.db import models
from django.utils import timezone

class Laudo(models.Model):
    municipio = models.CharField(max_length=100, verbose_name="Município")
    tipo_laudo = models.CharField(max_length=100, verbose_name="Tipo de Laudo")
    data_emissao = models.DateField(null=True, blank=True, verbose_name="Data de Emissão")
    tecnico = models.CharField(max_length=100, blank=True, verbose_name="Técnico")
    modalidade = models.CharField(max_length=100, blank=True, verbose_name="Modalidade")
    assentamento = models.CharField(max_length=100, blank=True, verbose_name="Assentamento")
    lote = models.CharField(max_length=50, blank=True, verbose_name="Lote")
    arquivo = models.CharField(max_length=255, blank=True, verbose_name="Arquivo")
    codigo_sipra = models.CharField(max_length=50, blank=True, verbose_name="Código SIPRA")

    class Meta:
        verbose_name = "Laudo"
        verbose_name_plural = "Laudos"

    def __str__(self):
        return f"{self.tipo_laudo} - {self.municipio} - {self.data_emissao}"

class DocumentoPGT(models.Model):
    tipo_documentopgt = models.CharField(max_length=100, verbose_name="Tipo de documento PGT")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    assentamento = models.CharField(max_length=100, blank=True, verbose_name="Assentamento")
    nome_t1 = models.CharField(max_length=100, blank=True, verbose_name="Nome T1")
    objetivo = models.CharField(max_length=100, blank=True, verbose_name="Objetivo")
    data_criacao = models.DateField(default=timezone.now, verbose_name="Data de Criação")
    codigo_sipra = models.CharField(max_length=50, blank=True, verbose_name="Código SIPRA")
    autenticador = models.CharField(max_length=255, blank=True, verbose_name="Autenticador")
    segundo_relatorio = models.CharField(max_length=10, default="Não", verbose_name="Segundo Relatório")

    class Meta:
        verbose_name = "Documento PGT"
        verbose_name_plural = "Documentos PGT"

    def __str__(self):
        return f"{self.tipo_documentopgt} - {self.municipio} - {self.assentamento}"

class DocumentoRecebido(models.Model):
    tipo_documento = models.CharField(max_length=100, verbose_name="Tipo de Documento")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    data_recebimento = models.DateField(default=timezone.now, verbose_name="Data de Recebimento")
    status = models.CharField(max_length=50, default="Recebido", verbose_name="Status")
    observacoes = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Documento Recebido"
        verbose_name_plural = "Documentos Recebidos"

    def __str__(self):
        return f"{self.tipo_documento} - {self.municipio} - {self.data_recebimento}"

class Parecer(models.Model):
    tipo_parecer = models.CharField(max_length=100, verbose_name="Tipo de Parecer")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    data_emissao = models.DateField(default=timezone.now, verbose_name="Data de Emissão")

    class Meta:
        verbose_name = "Parecer"
        verbose_name_plural = "Pareceres"

    def __str__(self):
        return f"{self.tipo_parecer} - {self.municipio} - {self.data_emissao}"

class Planilha(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    tipo = models.CharField(max_length=100, verbose_name="Tipo")
    data_criacao = models.DateField(default=timezone.now, verbose_name="Data de Criação")

    class Meta:
        verbose_name = "Planilha"
        verbose_name_plural = "Planilhas"

    def __str__(self):
        return f"{self.nome} - {self.tipo} - {self.data_criacao}"

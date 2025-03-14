# Generated by Django 5.1.6 on 2025-02-26 21:46

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=100, verbose_name='Tipo')),
                ('referencia', models.CharField(max_length=100, verbose_name='Referência')),
                ('data_emissao', models.DateField(verbose_name='Data de Emissão')),
                ('destinatario', models.CharField(max_length=200, verbose_name='Destinatário')),
                ('assunto', models.CharField(max_length=255, verbose_name='Assunto')),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='documentos/', verbose_name='Arquivo')),
            ],
            options={
                'verbose_name': 'Documento',
                'verbose_name_plural': 'Documentos',
                'ordering': ['-data_emissao'],
            },
        ),
        migrations.CreateModel(
            name='DocumentoRecebido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=100, verbose_name='Tipo')),
                ('referencia', models.CharField(max_length=100, verbose_name='Referência')),
                ('data_recebimento', models.DateField(verbose_name='Data de Recebimento')),
                ('remetente', models.CharField(max_length=200, verbose_name='Remetente')),
                ('assunto', models.CharField(max_length=255, verbose_name='Assunto')),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='documentos_recebidos/', verbose_name='Arquivo')),
            ],
            options={
                'verbose_name': 'Documento Recebido',
                'verbose_name_plural': 'Documentos Recebidos',
                'ordering': ['-data_recebimento'],
            },
        ),
        migrations.CreateModel(
            name='Laudo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=100, verbose_name='Número')),
                ('data', models.DateField(verbose_name='Data')),
                ('status', models.CharField(max_length=50, verbose_name='Status')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
            ],
            options={
                'verbose_name': 'Laudo',
                'verbose_name_plural': 'Laudos',
                'ordering': ['-data'],
            },
        ),
        migrations.CreateModel(
            name='PlanilhaMonitoramento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('periodo', models.CharField(max_length=50, verbose_name='Período')),
                ('data_atualizacao', models.DateField(default=django.utils.timezone.now, verbose_name='Data de Atualização')),
                ('responsavel', models.CharField(max_length=100, verbose_name='Responsável')),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='planilhas/', verbose_name='Arquivo')),
            ],
            options={
                'verbose_name': 'Planilha de Monitoramento',
                'verbose_name_plural': 'Planilhas de Monitoramento',
                'ordering': ['-data_atualizacao'],
            },
        ),
        migrations.CreateModel(
            name='Parecer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=100, verbose_name='Número')),
                ('data', models.DateField(verbose_name='Data')),
                ('conclusao', models.CharField(max_length=50, verbose_name='Conclusão')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='pareceres/', verbose_name='Arquivo')),
                ('laudo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pareceres', to='supervisao_ocupacional.laudo', verbose_name='Laudo')),
            ],
            options={
                'verbose_name': 'Parecer',
                'verbose_name_plural': 'Pareceres',
                'ordering': ['-data'],
            },
        ),
    ]

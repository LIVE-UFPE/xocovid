# Generated by Django 3.0.5 on 2020-05-03 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0028_delete_graficospredicao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='casoscidade',
            old_name='data_atualizacao',
            new_name='data_notificacao',
        ),
        migrations.RenameField(
            model_name='casoscidade',
            old_name='cidade',
            new_name='estado_residencia',
        ),
        migrations.RenameField(
            model_name='casoscidade',
            old_name='estado',
            new_name='municipio',
        ),
        migrations.RenameField(
            model_name='casosestado',
            old_name='data_atualizacao',
            new_name='data_notificacao',
        ),
        migrations.RenameField(
            model_name='casosestado',
            old_name='estado',
            new_name='estado_residencia',
        ),
    ]

# Generated by Django 3.0.5 on 2020-04-15 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0019_auto_20200410_0351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='bairro',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='cep',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='classificacao',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='coleta_amostra',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='coleta_exames',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='estado_notificacao',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='estado_residencia',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='evolucao',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='foi_outro_local_transmissao',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='internado',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='municipio',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='municipio_notificacao',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='outro_local_transmissao',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='paciente_hospitalizado',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='pais_residencia',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='sexo',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='situacao_notificacao',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='ventilacao_mecanica',
            field=models.CharField(max_length=50, null=True),
        ),
    ]

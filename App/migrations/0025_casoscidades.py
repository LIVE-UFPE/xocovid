# Generated by Django 3.0.5 on 2020-04-27 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0024_casosestado'),
    ]

    operations = [
        migrations.CreateModel(
            name='CasosCidades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_atualizacao', models.DateField(null=True)),
                ('estado', models.CharField(max_length=150, null=True)),
                ('cidade', models.CharField(max_length=150, null=True)),
                ('confirmados', models.IntegerField(null=True)),
                ('obitos', models.IntegerField(null=True)),
                ('populacao_estimada_2019', models.IntegerField(null=True)),
                ('confirmados_100k', models.FloatField(null=True)),
            ],
        ),
    ]

# Generated by Django 3.0.5 on 2020-04-09 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0017_accesskey'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesskey',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]

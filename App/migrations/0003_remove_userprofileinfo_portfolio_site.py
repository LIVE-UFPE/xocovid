# Generated by Django 3.0.4 on 2020-03-29 01:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_auto_20200328_1851'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='portfolio_site',
        ),
    ]

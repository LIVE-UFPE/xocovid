# Generated by Django 3.0.5 on 2020-05-13 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0037_userprofileinfo_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofileinfo',
            name='instituicao',
            field=models.CharField(max_length=150, null=True),
        ),
    ]

# Generated by Django 3.2 on 2022-01-13 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acoes', '0005_auto_20220111_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acao',
            name='data_hora_atualizacao',
            field=models.DateTimeField(auto_now=True, verbose_name='Última atualização'),
        ),
    ]

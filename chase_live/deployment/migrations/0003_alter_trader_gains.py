# Generated by Django 4.2.5 on 2023-09-21 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployment', '0002_trader_last_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trader',
            name='gains',
            field=models.CharField(default='0', max_length=20),
        ),
    ]

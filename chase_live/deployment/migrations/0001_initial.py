# Generated by Django 4.2.5 on 2023-09-20 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('gains', models.CharField(max_length=20)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=20)),
                ('qty', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=20)),
                ('gain', models.CharField(max_length=20)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deployment.trader')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pkid', models.CharField(max_length=40)),
                ('symbol', models.CharField(max_length=20)),
                ('qty', models.CharField(max_length=20)),
                ('side', models.CharField(max_length=20)),
                ('price', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
                ('submit', models.CharField(max_length=20)),
                ('fill', models.CharField(max_length=20)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deployment.trader')),
            ],
        ),
    ]
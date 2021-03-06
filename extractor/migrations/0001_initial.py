# Generated by Django 3.1.6 on 2021-02-05 21:33

from django.db import migrations, models
import django.utils.timezone
import extractor.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(default=extractor.models.gen_uuid, max_length=20, unique=True)),
                ('name', models.CharField(max_length=5000, verbose_name='Name')),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('successfully', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawalTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(default=extractor.models.gen_uuid, max_length=20, unique=True)),
                ('pan', models.CharField(max_length=16, verbose_name='PAN')),
                ('time', models.TimeField()),
                ('amount', models.FloatField(default=0.0)),
            ],
        ),
    ]

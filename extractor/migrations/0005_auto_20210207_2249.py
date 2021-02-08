# Generated by Django 3.1.6 on 2021-02-07 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extractor', '0004_remove_withdrawaltransaction_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawaltransaction',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='withdrawaltransaction',
            name='code',
            field=models.DecimalField(decimal_places=0, max_digits=6, verbose_name='Code'),
        ),
    ]

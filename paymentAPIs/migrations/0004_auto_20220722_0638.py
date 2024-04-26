# Generated by Django 3.2.8 on 2022-07-22 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paymentAPIs', '0003_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='callDuration',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='paymentId',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
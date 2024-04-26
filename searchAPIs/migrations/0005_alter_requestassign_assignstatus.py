# Generated by Django 3.2.8 on 2022-07-20 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searchAPIs', '0004_providerprogressnote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestassign',
            name='assignStatus',
            field=models.IntegerField(choices=[(1, 'Pending'), (2, 'Accepted'), (3, 'Rejected'), (4, 'completed'), (5, 'failed'), (6, 'cancelled'), (7, 'declined')], default=1),
        ),
    ]

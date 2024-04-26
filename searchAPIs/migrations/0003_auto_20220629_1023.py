# Generated by Django 3.2.8 on 2022-06-29 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searchAPIs', '0002_auto_20220615_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultantion',
            name='consultantionStatus',
            field=models.IntegerField(choices=[(1, 'pending'), (2, 'accepted'), (3, 'rejected'), (4, 'completed'), (5, 'failed'), (6, 'cancelled')]),
        ),
        migrations.AlterField(
            model_name='requestassign',
            name='assignStatus',
            field=models.IntegerField(choices=[(1, 'Pending'), (2, 'Accepted'), (3, 'Rejected'), (4, 'failed'), (6, 'cancelled')], default=1),
        ),
    ]

# Generated by Django 3.2 on 2022-08-25 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0026_auto_20220825_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='genderType',
            field=models.IntegerField(choices=[(1, 'He/Him'), (2, 'She/Her'), (3, 'They/Them')], null=True),
        ),
    ]
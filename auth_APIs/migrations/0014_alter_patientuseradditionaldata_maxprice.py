# Generated by Django 3.2.8 on 2022-06-23 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0013_user_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientuseradditionaldata',
            name='maxPrice',
            field=models.IntegerField(default=2000, null=True),
        ),
    ]

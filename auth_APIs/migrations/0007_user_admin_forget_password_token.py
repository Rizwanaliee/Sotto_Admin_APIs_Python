# Generated by Django 3.2.8 on 2022-06-06 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0006_provideruseradditionaldata_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='admin_forget_password_token',
            field=models.CharField(default=False, max_length=200, null=True),
        ),
    ]

# Generated by Django 3.2 on 2022-08-19 12:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0020_alter_provideruseradditionaldata_licensetypeid'),
    ]

    operations = [
        migrations.AddField(
            model_name='provideruseradditionaldata',
            name='createdAt',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AlterField(
            model_name='provideruseradditionaldata',
            name='licenseTypeId',
            field=models.ForeignKey(db_column='licenseTypeId', on_delete=django.db.models.deletion.CASCADE, related_name='licenseTypeIdData', to='auth_APIs.licensetype'),
        ),
    ]

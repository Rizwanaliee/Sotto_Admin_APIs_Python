# Generated by Django 3.2 on 2022-08-24 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0024_auto_20220824_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='provideruseradditionaldata',
            name='licenseName',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='provideruseradditionaldata',
            name='licenseNumber',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='provideruseradditionaldata',
            name='licenseTypeId',
            field=models.ForeignKey(db_column='licenseTypeId', default=1, on_delete=django.db.models.deletion.CASCADE, related_name='licenseTypeIdData', to='auth_APIs.licensetype'),
            preserve_default=False,
        ),
    ]

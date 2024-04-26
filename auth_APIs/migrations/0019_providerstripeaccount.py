# Generated by Django 3.2.8 on 2022-08-13 05:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0018_auto_20220810_1046'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderStripeAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stipeAccountId', models.CharField(max_length=255)),
                ('isCompleted', models.BooleanField(default=False)),
                ('refreshUrl', models.CharField(blank=True, max_length=255, null=True)),
                ('returnUrl', models.CharField(blank=True, max_length=255, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('userId', models.OneToOneField(db_column='userId', on_delete=django.db.models.deletion.CASCADE, related_name='provider_stipe_ref', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'provider_stripe_accounts',
            },
        ),
    ]
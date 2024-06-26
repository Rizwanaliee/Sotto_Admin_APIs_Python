# Generated by Django 3.2.8 on 2022-07-06 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedCardDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentMethodId', models.CharField(max_length=255)),
                ('cardStatus', models.IntegerField(choices=[(1, 'ordinary'), (2, 'default')], default=1)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('userId', models.ForeignKey(db_column='userId', on_delete=django.db.models.deletion.CASCADE, related_name='customerCard', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'CardDetails',
            },
        ),
    ]

# Generated by Django 3.2 on 2022-09-21 06:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('searchAPIs', '0005_alter_requestassign_assignstatus'),
        ('ratingAndReview', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratingandreview',
            name='consultationId',
            field=models.OneToOneField(db_column='consultationId', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rating_to_consultationId', to='searchAPIs.consultantion'),
        ),
    ]
# Generated by Django 5.0.3 on 2024-05-11 05:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_rename_active_listing_listing_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='watchlist',
            field=models.ManyToManyField(blank=True, null=True, related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]

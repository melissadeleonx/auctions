# Generated by Django 5.0.3 on 2024-05-05 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_remove_listing_image_url_listing_active_listing_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='seller_Notes',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
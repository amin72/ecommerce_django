# Generated by Django 3.0.2 on 2020-01-18 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_item_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='This is item description.'),
            preserve_default=False,
        ),
    ]

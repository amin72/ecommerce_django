# Generated by Django 3.0.2 on 2020-01-18 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]

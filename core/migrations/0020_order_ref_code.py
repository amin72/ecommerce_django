# Generated by Django 3.0.2 on 2020-01-23 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20200123_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(blank=True, max_length=24, null=True),
        ),
    ]

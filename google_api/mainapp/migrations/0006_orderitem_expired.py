# Generated by Django 4.1.7 on 2023-03-24 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_alter_updateexecution_document_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='expired',
            field=models.BooleanField(default=False, help_text='Delivery expiration status of the item'),
        ),
    ]

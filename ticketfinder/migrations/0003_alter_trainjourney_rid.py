# Generated by Django 5.0.4 on 2024-05-02 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketfinder', '0002_trainjourney_alter_trainstation_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainjourney',
            name='rid',
            field=models.CharField(max_length=20, verbose_name='Train RTTI Identifier'),
        ),
    ]

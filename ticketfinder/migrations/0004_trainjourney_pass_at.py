# Generated by Django 5.0.4 on 2024-05-08 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketfinder', '0003_alter_trainjourney_rid'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainjourney',
            name='pass_at',
            field=models.TimeField(blank=True, null=True, verbose_name='Actual Passing Time'),
        ),
    ]

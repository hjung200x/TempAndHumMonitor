# Generated by Django 4.1.2 on 2022-10-15 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_alter_monitor_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor',
            name='date',
            field=models.CharField(max_length=21),
        ),
    ]

# Generated by Django 4.1.2 on 2022-10-15 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigTbl',
            fields=[
                ('name', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=64)),
            ],
        ),
    ]

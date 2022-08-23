# Generated by Django 3.2.14 on 2022-07-28 18:59

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lida2',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('num', models.IntegerField(blank=True, null=True)),
                ('nombre', models.CharField(blank=True, max_length=256, null=True)),
                ('anho', models.IntegerField(blank=True, null=True)),
                ('long', models.IntegerField(blank=True, null=True)),
                ('lat', models.IntegerField(blank=True, null=True)),
                ('color', models.CharField(blank=True, max_length=256, null=True)),
                ('orig_srid', models.CharField(blank=True, max_length=256, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=25830)),
            ],
            options={
                'db_table': 'lida2',
            },
        ),
    ]

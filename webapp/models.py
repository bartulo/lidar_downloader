# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class Lida2(models.Model):
    id = models.IntegerField(primary_key=True)
    num = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=256, blank=True, null=True)
    anho = models.IntegerField(blank=True, null=True)
    long = models.IntegerField(blank=True, null=True)
    lat = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=256, blank=True, null=True)
    orig_srid = models.CharField(max_length=256, blank=True, null=True)
    geom = models.PolygonField(srid=25830, blank=True, null=True)
    tam = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'lida2'

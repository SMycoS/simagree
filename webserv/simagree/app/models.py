# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Apparition(models.Model):
    id = models.AutoField(primary_key=True)
    taxon = models.ForeignKey('Identifiants', models.DO_NOTHING, db_column='taxon')
    date = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'apparition'


class Identifiants(models.Model):
    id = models.AutoField(primary_key=True)
    taxon = models.DecimalField(unique=True, max_digits=65535, decimal_places=65535)
    fiche = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    comestible = models.TextField(blank=True, null=True)
    sms = models.NullBooleanField()
    a_imprimer = models.NullBooleanField()
    lieu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'identifiants'


class Nomenclature(models.Model):
    id = models.AutoField(primary_key=True)
    taxon = models.ForeignKey(Identifiants, models.DO_NOTHING, db_column='taxon')
    codesyno = models.SmallIntegerField()
    genre = models.TextField()
    espece = models.TextField()
    variete = models.TextField(blank=True, null=True)
    forme = models.TextField(blank=True, null=True)
    autorite = models.TextField()
    moser = models.TextField()
    biblio1 = models.TextField(blank=True, null=True)
    biblio2 = models.TextField(blank=True, null=True)
    biblio3 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nomenclature'


class Noms(models.Model):
    id = models.AutoField(primary_key=True)
    taxon = models.ForeignKey(Identifiants, models.DO_NOTHING, db_column='taxon')
    nom = models.TextField()

    class Meta:
        managed = False
        db_table = 'noms'


class NotesEco(models.Model):
    id = models.AutoField(primary_key=True)
    taxon = models.ForeignKey(Identifiants, models.DO_NOTHING, db_column='taxon', unique=True)
    notes = models.TextField()
    ecologie = models.TextField()

    class Meta:
        managed = False
        db_table = 'notes_eco'


class Themes(models.Model):
    id = models.AutoField(primary_key=True)
    taxon = models.ForeignKey(Identifiants, models.DO_NOTHING, db_column='taxon')
    theme = models.TextField()

    class Meta:
        managed = False
        db_table = 'themes'

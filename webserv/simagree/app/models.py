from django.db import models


class Themes(models.Model):
    id = models.AutoField(primary_key=True)
    theme = models.TextField()

    class Meta:
        managed = True
        db_table = 'themes'

class Identifiants(models.Model):
    taxon = models.IntegerField(unique=True)
    noms = models.TextField(blank=True, null=True)
    fiche = models.IntegerField(blank=True, null=True)
    comestible = models.TextField(blank=True, null=True)
    sms = models.NullBooleanField()
    a_imprimer = models.NullBooleanField()
    lieu = models.TextField(blank=True, null=True)
    apparition = models.TextField()


    class Meta:
        managed = True
        db_table = 'identifiants'


class Nomenclature(models.Model):
    taxon = models.ForeignKey(Identifiants, on_delete=models.CASCADE, to_field='taxon')
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
        managed = True
        db_table = 'nomenclature'


class NotesEco(models.Model):
    taxon = models.ForeignKey(Identifiants, on_delete=models.CASCADE, to_field='taxon')
    notes = models.TextField()
    ecologie = models.TextField()

    class Meta:
        managed = True
        db_table = 'notes_eco'



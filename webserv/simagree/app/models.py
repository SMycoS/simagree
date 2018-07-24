from django.db import models


class Themes(models.Model):
    theme = models.TextField(unique = True)

    def __unicode__(self):
        return self.theme
    
    def __str__(self):
        return self.theme

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
    notes = models.TextField(blank = True, null = True)
    ecologie = models.TextField(blank = True, null = True)
    theme1 = models.ForeignKey(Themes, on_delete = models.SET_NULL, null = True, to_field='theme', related_name='Theme1')
    theme2 = models.ForeignKey(Themes, on_delete = models.SET_NULL, null = True, to_field='theme', related_name='Theme2')
    theme3 = models.ForeignKey(Themes, on_delete = models.SET_NULL, null = True, to_field='theme', related_name='Theme3')
    theme4 = models.ForeignKey(Themes, on_delete = models.SET_NULL, null = True, to_field='theme', related_name='Theme4')
    icono1 = models.TextField(blank = True, null = True)
    icono2 = models.TextField(blank = True, null = True)
    icono3 = models.TextField(blank = True, null = True)
    num_herbier = models.IntegerField(blank = True, null = True)
    


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
    date = models.DateField(auto_now = True)

    class Meta:
        managed = True
        db_table = 'nomenclature'

class LieuRecolte:
    libelle = models.TextField(unique = True)
    commune = models.TextField()
    lieu_dit = models.TextField()

    class Meta:
        managed = True
        db_table = 'lieurec'

class ListeRecolte(models.Model):
    date = models.DateField()
    lieu = models.TextField()
    taxons = models.ManyToManyField(Identifiants)

    class Meta:
        managed = True
        db_table = 'listrec'


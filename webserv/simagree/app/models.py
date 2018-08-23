from django.db import models


class Themes(models.Model):
    theme = models.TextField(unique = True)
    titre = models.TextField(blank = True, null = True)

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
    sms = models.NullBooleanField()
    comestible = models.TextField(blank=True, null=True)
    a_imprimer = models.NullBooleanField()
    apparition = models.TextField(blank=True, null=True)
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
    autorite = models.TextField(blank=True, null=True)
    biblio1 = models.TextField(blank=True, null=True)
    biblio2 = models.TextField(blank=True, null=True)
    biblio3 = models.TextField(blank=True, null=True)
    moser = models.TextField(blank=True, null=True)
    date = models.DateField(blank = True, null = True)

    class Meta:
        managed = True
        db_table = 'nomenclature'

class Classification(models.Model):
    genre = models.TextField()
    regne = models.TextField(blank = True, null = True)
    embranchement = models.TextField(blank = True, null = True)
    classe = models.TextField(blank = True, null = True)
    ordre = models.TextField(blank = True, null = True)
    famille = models.TextField(blank = True, null = True)

    class Meta:
        managed = True
        db_table = 'classification'

class LieuRecolte(models.Model):
    commune = models.TextField()
    lieu_dit = models.TextField()
    libelle = models.TextField(unique = True)

    def __unicode__(self):
        return self.libelle
    
    def __str__(self):
        return self.libelle

    class Meta:
        managed = True
        db_table = 'lieurec'
    
class ObjetRecolte(models.Model):
    taxon = models.ForeignKey(Identifiants, on_delete = models.CASCADE)
    recolteur = models.TextField(blank = True, null = True)
    determinateur = models.TextField(blank = True, null = True)
    num_herbier = models.IntegerField(blank = True, null = True) 

    class Meta:
        managed = True
        db_table = 'objrec'

class ListeRecolte(models.Model):
    date = models.DateField()
    lieu = models.ForeignKey(LieuRecolte, on_delete=models.SET_NULL, null=True, blank=True)
    taxons = models.ManyToManyField(ObjetRecolte)

    class Meta:
        managed = True
        db_table = 'listrec'


import csv
from .models import Identifiants, Themes, Nomenclature

# Identifiants
def replaceIdentifiants():

    # Ouverture du CSV
    file = open('SMSIdent.csv', 'r')

    # Lecture du CSV
    rows = csv.reader(file, delimiter=';')
    # Itération sur les lignes
    for item in rows:
        # Création d'un objet
        obj = Identifiants(
            taxon = int(item[0]),
            sms = bool(item[1]),
            comestible = item[2],
            fiche = int(item[3]),
            a_imprimer = bool(item[4]);
            apparition = item[5],
            noms = item[6], 
            notes = item[7],
            ecologie = item[8],
            icono1 = item[13],
            icono2 = item[14],
            icono3 = item[15],
            num_herbier = item[16]
        )
        
        # Sauvegarde de l'objet
        obj.save(using = 'simagree')
        
        # Fermeture du fichier
        file.close()


# Nomenclature
def replaceNomenclature():
    file = open('SMSNom.csv', 'r')
    rows = csv.reader(file, delimiter=';')
    for item in rows:
        obj = Nomenclature(
            taxon = int(item[0]),
            codesyno = int(item[1]),
            genre = item[2],
            espece = item[3],
            variete = item[4],
            forme = item[5],
            autorite = item[6],
            moser = item[7],
            bilbio1 = item[8],
            biblio2 = item[9],
            biblio3 = item[10],
        )
        obj.save(using = 'simagree')
        file.close()
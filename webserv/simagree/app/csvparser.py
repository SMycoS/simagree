import csv
from .models import Identifiants, Themes, Nomenclature

# Identifiants
def replaceIdentifiants(file):

    # Ouverture du CSV
    #file = open(filename, 'r')

    # Lecture du CSV
    rows = csv.reader(file, delimiter=';')
    # On passe la première colonne (headers du csv)
    next(rows, None)
    elements = []

    # Itération sur les lignes
    for item in rows:
        # Création d'un objet
        # Initialisation avec les valeurs obligatoires et les champs texte
        obj = Identifiants(
            taxon = int(item[0]),
            sms = bool(item[1]),
            comestible = item[2],
            a_imprimer = bool(item[4]),
            apparition = item[5],
            noms = item[6], 
            notes = item[7],
            ecologie = item[8],
            icono1 = item[13],
            icono2 = item[14],
            icono3 = item[15],
        )
        if (item[3]):
            obj.fiche = int(item[3])
        if (item[16]):
            obj.num_herbier = int(item[16])
        

        # Sauvegarde de l'objet
        elements.append(obj)
        
    # Fermeture du fichier
    file.close()
    Identifiants.objects.using('simagree').bulk_create(elements)


# Nomenclature
def replaceNomenclature(file):
    #file = open(filename, 'r')
    rows = csv.reader(file, delimiter=';')
    next(rows, None)
    old_taxon = 0
    elements = []
    for item in rows:
        # on récupère le taxon courant
        if(item[0] == ''):
            continue
        current_taxon = int(item[0])
        if old_taxon != current_taxon:
            ident_instance = Identifiants.objects.using('simagree').get(taxon = current_taxon)
            old_taxon = current_taxon
        
        obj = Nomenclature(
            taxon = ident_instance,
            codesyno = int(item[1]),
            genre = item[2],
            espece = item[3],
            variete = item[4],
            forme = item[5],
            autorite = item[6],
            biblio1 = item[7],
            biblio2 = item[8],
            biblio3 = item[9],
            moser = item[10]
        )
        elements.append(obj)
    file.close()
    Nomenclature.objects.using('simagree').bulk_create(elements)

# Fonction de test
def testCsv(filee):
    rows = csv.reader(filee, delimiter=';')
    next(rows, None)
    for item in rows:
        print(item)
    filee.close()

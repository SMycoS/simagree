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
    
    '''
    Les éléments sont d'abord créés comme objets python stockés dans une liste,
    puis sauvegardés dans la db via la méthode bulk_create des modèles django.
    Cela permet de réduire le nombre d'appels à la db (1 contre n en procédant
    objet par objet).
    '''
    elements = []
    theme_list = [] # liste des thèmes (string)
    theme_list_instance = [] # liste des thèmes (instance)

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
        
        # Ajout des thèmes dans la liste

        for cpt,theme in enumerate([item[9], item[10], item[11], item[12]]):
            if theme not in theme_list and theme != "":
                theme_list.append(theme)
                theme_instance = Themes(theme = theme)
                theme_list_instance.append(theme_instance)
            if theme != "":
                if cpt == 0:
                    obj.theme1 = theme_instance
                elif cpt == 1:
                    obj.theme2 = theme_instance
                elif cpt == 2:
                    obj.theme3 = theme_instance
                elif cpt == 3:
                    obj.theme4 = theme_instance
            

        # Sauvegarde de l'objet dans la liste
        elements.append(obj)
        
    # Fermeture du fichier
    file.close()

    # Création des objets Theme
    Themes.objects.using('simagree').bulk_create(theme_list_instance)
    # Création des objets Identifiants
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

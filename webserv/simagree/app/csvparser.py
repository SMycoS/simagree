import csv, datetime
from .models import Identifiants, Themes, Nomenclature, Classification
import traceback

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
    # dictionnaire des thèmes
    theme_dict =  Themes.objects.all()
    theme_dict = {t.theme : t for t in theme_dict}
    # compteur de thèmes ajoutés
    added_themes = 0
    # liste des instances de thèmes ajoutés
    theme_list_instance = []

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
            if theme not in theme_dict.keys() and theme != "":
                theme_dict[theme] = Themes(theme = theme)
                added_themes += 1
                theme_list_instance.append(theme_dict[theme])
            if theme != "":
                if cpt == 0:
                    obj.theme1 = theme_dict[theme]
                elif cpt == 1:
                    obj.theme2 = theme_dict[theme]
                elif cpt == 2:
                    obj.theme3 = theme_dict[theme]
                elif cpt == 3:
                    obj.theme4 = theme_dict[theme]
            

        # Sauvegarde de l'objet dans la liste
        elements.append(obj)
        
    # Fermeture du fichier
    file.close()

    # Création des objets Theme (si la liste des instances n'est pas vide)
    if added_themes > 0:
        Themes.objects.using('import-check').all().delete()
        Themes.objects.using('import-check').bulk_create(theme_list_instance)
        Themes.objects.bulk_create(theme_list_instance)
        Theme.objects.using('cimetiere').bulk_create(theme_list_instance)

    # Création des objets Identifiants

    # On commence par essayer l'insertion dans une base secondaire (supposée vide)
    try:
        Identifiants.objects.using('import-check').all().delete()
        Identifiants.objects.using('import-check').bulk_create(elements)
    except:
        # On retourne False s'il y a une erreur (gérée ensuite dans les vues)
        return False
    else:
        # Si le test passe, on vide la base secondaire et la base principale, puis on insète dans la base principale
        # Logiquement, il n'y aura pas d'erreur
        Identifiants.objects.all().delete()
        Identifiants.objects.bulk_create(elements)
        return True


        


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
            ident_instance = Identifiants.objects.get(taxon = current_taxon)
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
            moser = item[10],
            date = datetime.datetime.strptime(item[11], '%d/%m/%Y').strftime('%Y-%m-%d')
        )
        elements.append(obj)
    file.close()

    try:
        Nomenclature.objects.using('import-check').all().delete()
        Nomenclature.objects.using('import-check').bulk_create(elements)
    except:
        traceback.print_exc()
        return False
    else:
        Nomenclature.objects.all().delete()
        Nomenclature.objects.bulk_create(elements)
        return True

def replaceClassification(file):
    rows = csv.reader(file, delimiter=';')
    next(rows, None)
    old_taxon = 0
    elements = []
    for item in rows:
        obj = Classification(
            regne = item[0],
            embranchement = item[1],
            classe = item[2],
            ordre = item[3],
            famille = item[4],
            genre = item[5]
        )
        elements.append(obj)
    
    try:
        Classification.objects.using('import-check').all().delete()
        Classification.objects.using('import-check').bulk_create(elements)
    except:
        traceback.print_exc()
        return False
    else:
        Classification.objects.all().delete()
        Classification.objects.bulk_create(elements)
        return True
    
    

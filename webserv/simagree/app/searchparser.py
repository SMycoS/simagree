# Parsing des options de recherche

from .models import Identifiants, NotesEco, Themes, Nomenclature

# initie la requête à la BDD simagree
# l'argument data est la forme nettoyée (cleaned_data) du formulaire de recherche
def dbRequest(data):

    # préparation de la requête
    query = Nomenclature.objects.using('simagree').select_related('taxon')

    # agrégation de filtres

    # options checkables
    if (not data['displaySyno']):
        query = query.filter(codesyno=0) # uniquement nom principal
    if (data['presentSms']):
        query = query.filter(taxon__sms=True)
    
    # filtres sur les champs texte
    if (data['nomUsuel']):
        query = query.filter(taxon__noms__icontains=data['nomUsuel'])
    if (data['genre']):
        query = query.filter(genre__icontains=data['genre'])
    if (data['espece']):
        query = query.filter(espece__icontains=data['espece'])

    # selecteur comestible
    if (data['comestible'] == 'yes'):
        query = query.filter(taxon__comestible='C')
    elif (data['comestible'] == 'no'):
        query.exclude(taxon__comestible='C')

    
    # la requête n'est effectuée qu'une seule fois, ci-dessous
    return query.order_by('taxon').values(
        'taxon_id',
        'genre',
        'espece',
        'variete',
        'forme',
        'taxon__sms',
        'taxon__comestible',
        'taxon__noms'
        )
                        
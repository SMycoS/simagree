# Parsing des options de recherche

from .models import Identifiants, Themes, Nomenclature

# initie la requête à la BDD simagree
# l'argument data est la forme nettoyée (cleaned_data) du formulaire de recherche
# l'argument size est un double (nb par page, page)
# renvoie le nombre total de résultats sans offset/limite et les résultats


def dbRequest(data, size):
  # calcul de l'offset et de la limite
  offset = (size[1] - 1) * size[0]
  limit = size[0] * size[1]

  # préparation de la requête
  query = Nomenclature.objects.select_related('taxon')

  # agrégation de filtres

  # options checkables
  if (not data['displaySyno']):
    query = query.filter(codesyno=0)  # uniquement nom principal
  if (data['presentSms']):
    query = query.filter(taxon__sms=True)
  if (data['a_imprimer']):
    query = query.filter(taxon__a_imprimer=True)

  # filtre taxon
  if (data['taxon']):
    query = query.filter(taxon__taxon__istartswith=data['taxon'])
  if (data['fiche']):
    query = query.filter(taxon__fiche__istartswith=data['fiche'])

  # filtres sur les champs texte
  if (data['nomUsuel']):
    query = query.filter(taxon__noms__icontains=data['nomUsuel'])
  if (data['genre']):
    query = query.filter(genre__icontains=data['genre'])
  if (data['espece']):
    query = query.filter(espece__icontains=data['espece'])

  # selecteur comestible
  if data['comestible'] != 'all':
    query = query.filter(taxon__comestible=data['comestible'])

  # la requête n'est effectuée qu'une seule fois, ci-dessous
  return (
      query.count(),
      query.order_by('taxon_id', 'codesyno').values(
          'taxon_id',
          'genre',
          'espece',
          'variete',
          'forme',
          'taxon__sms',
          'taxon__comestible',
          'taxon__fiche',
          'id',
          'codesyno',
          'autorite'
      )[offset:limit]
  )


def light_dbRequest(data):
  # préparation de la requête
  query = Nomenclature.objects.select_related('taxon')

  if not(data['genre']) and not(data['espece']):
    return []

  # filtres sur les champs texte
  if (data['genre']):
    query = query.filter(genre__icontains=data['genre'])
  if (data['espece']):
    query = query.filter(espece__icontains=data['espece'])

  # la requête n'est effectuée qu'une seule fois, ci-dessous
  return query.order_by('taxon_id', 'codesyno').values(
      'taxon_id',
      'genre',
      'espece',
      'variete',
      'forme',
      'taxon__noms'
  )


def light_dbRequest_bis(data, size):
  # calcul de l'offset et de la limite
  offset = (size[1] - 1) * size[0]
  limit = size[0] * size[1]
  # préparation de la requête
  query = Nomenclature.objects.select_related('taxon')

  # filtres sur les champs texte
  if (data['genre']):
    query = query.filter(genre__icontains=data['genre'])
  if (data['espece']):
    query = query.filter(espece__icontains=data['espece'])

  # la requête n'est effectuée qu'une seule fois, ci-dessous
  return (
      query.count(),
      query.order_by('taxon_id', 'codesyno').values(
          'taxon_id',
          'genre',
          'espece',
          'variete',
          'forme',
          'taxon__noms'
      )[offset:limit]
  )

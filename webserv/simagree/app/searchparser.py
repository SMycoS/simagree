# Parsing des options de recherche

from .models import Identifiants, NotesEco, Themes, Nomenclature

class searchParse():

    def __init__(self):
        self.genre = ''
        self.espece = ''
        self.nom = ''
        self.sms = False
        self.syno = False

        self.opts = {
            'taxon' : 'taxon_id',
            'genre' : 'genre',
            'espece' : 'espece',
            'noms' : 'taxon__noms',
            'sms' : 'taxon__sms'
        }
    
    

    def initRequest(self):
        # A compléter
        return Nomenclature.objects.using('simagree').select_related('taxon').values(**self.opts)
        
        
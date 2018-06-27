

class MyList():
    liste = [{
        'taxon' : 401,
        'nom' : 'foobar',
        'genre' : 'fooescens',
        'espece' : 'barinata',
        'com' : 'toxique',
        'sms' : True
    },
    {
        'taxon' : 402,
        'nom' : 'foobar',
        'genre' : 'fooescens',
        'espece' : 'barinata',
        'com' : 'toxique',
        'sms' : True
    },{
        'taxon' : 401,
        'nom' : 'foobar',
        'genre' : 'aaa',
        'espece' : 'bbb',
        'com' : 'oui',
        'sms' : False
    }]

    @classmethod
    def getShrooms(self):
        return self.liste
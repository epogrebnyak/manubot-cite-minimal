from dataclasses import dataclass
 
"""
Citation pipeline:

    CiteKey -> Handle -> CSL_Dict
    CiteKey('doi:10/gf8gkw') -> DOI('10.1038/171737a0') -> {'title': ...}

ci = CiteKey('doi:10.1038/171737a0').handle().csl_dict()
assert ci['title'].startswith('Molecular Structure of Nucleic Acids')
assert standardize_citekey('doi:10/gf8gkw') == 'doi:10.1038/d41586-019-02781-4'
assert citekey_to_csl_item('doi:10/gf8gkw')['title'] == \
    'How to make computing more sustainable'
"""

class CitekeyParsingError(Exception):
    pass


def constructor(prefix: str):
    try:
        key = prefix.lower()
        return Handle.mapper()[key]
    except KeyError:            
      prefixes = list(Handle.mapper().keys())
      raise CitekeyParsingError(f'Prefix {prefix} not supported.\n'  
                                f'Must be one of {prefixes}')

    
def split_prefixed_identifier(string: str):
    trimmed = string[1:] if string.startswith('@') else string
    try:    
       source, identifier = trimmed.split(':', 1)
    except ValueError:   
       raise CitekeyParsingError(f"Could not process '{string}' as citekey.")
    constructor(source) # will raise error on wrong prefix
    return source, identifier
   

class CiteKey(object):  
    def __init__(self, value):
        self.source, self.identifier = split_prefixed_identifier(value)
    
    def handle(self):        
        constr = constructor(self.source)
        return constr(self.identifier)  

    def __str__(self):
        return f'{self.source}:{self.identifier}'
    
    def __repr__(self):
        return "CiteKey(value='{}')".format(self)

@dataclass
class CiteTuple(CiteKey):
    source: str
    identifier: str 

    def citekey(self):      
       return CiteKey(str(self))  
    
class CSL_Dict(dict):
    def __init__(self, incoming_dict: dict):
        super().__init__(incoming_dict)
        
    def add_note(self):
        return self
    
    def generate_id(self):
        """If no id, make a hash"""
        return self        
    
    def _set_id(self, x):
        self['id'] = x
        return self
    
    def fix_type(self):
        return self
    
    def prune(self):
        return self 

    def minimal(self):
        keys = ('title author URL issued type container-title' 
                'volume issue page DOI').split()
        return CSL_Dict({k: v for k, v in self.items() if k in keys})          

   
@dataclass
class Handle:
    identifier: str
    
    def standardize(self):  
        return self
    
    def csl_dict(self):
        return self
    
    def citekey(self):
        prefix = self.__class__.__name__.lower()
        return CiteTuple(prefix, self.identifier).citekey()
 
    @classmethod
    def mapper(cls):
        return {cls.__name__.lower(): cls for cls in Handle.__subclasses__()}


class PMID(Handle):
    pass       


class PMCID(Handle):
    pass 


class Arxiv(Handle):
    pass 


class URL(Handle):
    pass 


class Wikidata(Handle):    
    pass


class ISBN(Handle):    
    def standardize(self):
        from isbnlib import to_isbn13
        self.identifier = to_isbn13(self.identifier)
        return self


class DOI(Handle):
    def csl_dict(self):
        from manubot.cite.doi import get_doi_csl_item
        return CSL_Dict(get_doi_csl_item(self.identifier))
    
    def standardize(self):
        from manubot.cite.doi import expand_short_doi
        if self.identifier.startswith('10/'):           
           self.identifier = expand_short_doi(self.identifier)
        return self

    
def standardize_citekey(citekey: str) -> str:
    obj = CiteKey(citekey).handle().standardize().citekey()
    return str(obj) 


def citekey_to_csl_item(citekey: str, prune=True) -> dict:
    """
    Generate a CSL item (Python dictionary) for the input *citekey* string.
    """
    csl_item = CiteKey(citekey).handle().standardize().csl_dict()
    csl_item.fix_type()
    csl_item.add_note()
    csl_item.generate_id()
    if prune:
        csl_item.prune()
    return csl_item

ci = CiteKey('doi:10.1038/171737a0').handle().csl_dict()
assert ci['title'].startswith('Molecular Structure of Nucleic Acids')
assert standardize_citekey('doi:10/gf8gkw') == 'doi:10.1038/d41586-019-02781-4'
assert citekey_to_csl_item('doi:10/gf8gkw') == {'indexed': {'date-parts': [[2019, 9, 18]],
  'date-time': '2019-09-18T16:41:01Z',
  'timestamp': 1568824861950},
 'reference-count': 0,
 'publisher': 'Springer Science and Business Media LLC',
 'issue': '7774',
 'license': [{'URL': 'http://www.springer.com/tdm',
   'start': {'date-parts': [[2019, 9, 1]],
    'date-time': '2019-09-01T00:00:00Z',
    'timestamp': 1567296000000},
   'delay-in-days': 0,
   'content-version': 'tdm'}],
 'content-domain': {'domain': [], 'crossmark-restriction': False},
 'published-print': {'date-parts': [[2019, 9]]},
 'DOI': '10.1038/d41586-019-02781-4',
 'type': 'article-journal',
 'created': {'date-parts': [[2019, 9, 18]],
  'date-time': '2019-09-18T16:06:24Z',
  'timestamp': 1568822784000},
 'page': '310-310',
 'source': 'Crossref',
 'is-referenced-by-count': 0,
 'title': 'How to make computing more sustainable',
 'prefix': '10.1038',
 'volume': '573',
 'member': '297',
 'published-online': {'date-parts': [[2019, 9, 18]]},
 'container-title': 'Nature',
 'original-title': [],
 'language': 'en',
 'link': [{'URL': 'http://www.nature.com/articles/d41586-019-02781-4.pdf',
   'content-type': 'application/pdf',
   'content-version': 'vor',
   'intended-application': 'text-mining'},
  {'URL': 'http://www.nature.com/articles/d41586-019-02781-4',
   'content-type': 'text/html',
   'content-version': 'vor',
   'intended-application': 'text-mining'},
  {'URL': 'http://www.nature.com/articles/d41586-019-02781-4.pdf',
   'content-type': 'application/pdf',
   'content-version': 'vor',
   'intended-application': 'similarity-checking'}],
 'deposited': {'date-parts': [[2019, 9, 18]],
  'date-time': '2019-09-18T16:07:00Z',
  'timestamp': 1568822820000},
 'score': 1.0,
 'subtitle': [],
 'short-title': [],
 'issued': {'date-parts': [[2019, 9]]},
 'references-count': 0,
 'journal-issue': {'published-print': {'date-parts': [[2019, 9]]},
  'issue': '7774'},
 'alternative-id': ['CM17175824'],
 'URL': 'https://doi.org/gf8gkw',
 'relation': {},
 'ISSN': ['0028-0836', '1476-4687'],
 'subject': ['Multidisciplinary'],
 'container-title-short': 'Nature'}


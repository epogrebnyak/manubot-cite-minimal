"""
    str -> Citation (raw) -> Citation (standard) -> CSL_Item (raw) ->
           CSL_Item (with id, brushed)-> csl_style -> str
    ```
    The cite key journey:
    - from string we can extract citekeys which follow source:identifier pattern
    - source:identifier becomes an instance of DOI(identifier), ISBN(identifier), 
      etc, collectively referered as 'citations' 
    - DOI, ISBN, etc can be normalised (eg short DOI becomes regular DOI)  
    - from citation we can get bibliographic information - retrieve() method
      returns a `CitationItem` dictionary csl_item       
    - the citation item is refined (add id, purge fileds not accepts by 
      pandoc-citeproc, etc)
    - with optional csl_style and format we get a string of bibliography 
    
    From citations.tsv:

    string	citation	standard_citation	citation_id
    @doi:10/ccg94v	doi:10/ccg94v	doi:10.1038/scientificamerican0490-56	1GSTJk5bl
"""

"""
- text
- CiteKey (source, identifier) tuple
- Citation (parent of DOI ISBN PMID Arxiv)
- CiteItem (csl_item)
- text
"""

text = """
[@doi:10.1038/171737a0]
[@doi:10/ccg94v]
"""

d1 = DOI('10.1038/171737a0') # Watson Crick DNA
d2 = DOI('10/ccg94v') # Kary Mullis PCR    

from dataclasses import dataclass

@dataclass
class CiteKey:
    source: str
    identifier: str
    
@dataclass
class Citation:
    identifier: str

    def normalise(self):
        pass
        return self 

    def retrieve(self):
        pass
        return CiteItem({})
    
    
class CiteItem(dict):
    def __init__(self, dict_):
        super().__init__(dict_)
        
    def add_id(self):
        return self
    
    def prune(self):
        return self
    
class DOI(Citation):    
    pass

class ISBN(Citation):    
    pass

class PMID(Citation):    
    pass

class Arxiv(Citation):    
    pass

def extract_citekeys(text: str):
    return [CiteKey('doi', '10.1038/171737a0'),
            CiteKey('doi', '10/ccg94v')]

def to_citation(citekey):
    lookup = dict(doi=DOI, isbn=ISBN, pmid=PMID, arxiv=Arxiv)
    return lookup[citekey.source](citekey.identifier)

def make_bibliography(csl_list, csl_style):
    pass

def from_manuscript(text: str, csl_style=None, output_format='plain'):
    """Return bibliography list based on text with [@citekeys]."""    
    citekeys = extract_citekeys(text)
    citations = [to_citation(citekey) for citekey in citekeys]    
    citations = [citation.normalise() for citation in citations]
    csl_list = [citation.retrieve() for citation in citations]
    csl_list = [csl_item.add_id().prune() for csl_item in csl_list]
    return make_bibliography(csl_list, csl_style)
    
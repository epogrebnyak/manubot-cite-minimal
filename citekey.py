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
    constructor(source)  # will raise error on wrong prefix
    return source, identifier


class CiteKey(object):
    def __init__(self, citekey):
        self.source, self.identifier = split_prefixed_identifier(citekey)

    def tuple(self):
        return CiteTuple(self.source, self.identifier)

    def handle(self):
        constr = constructor(self.source)
        return constr(self.identifier)

    def str(self):
        return str(self)

    def __str__(self):
        return f'{self.source}:{self.identifier}'

    def __repr__(self):
        return "CiteKey(value='{}')".format(self)

    def detag(self):
        pass


@dataclass
class CiteTuple(CiteKey):
    """Proxy dataclass to hold .source and .identifier as separate attributes
       and be able to pass them to constructor.

       Useful as CiteTuple(source, identifier).citekey()

       Reason to exist: we wanted CiteKey to accept full citekey string in its
                        constructor as CiteKey('doi:10/gf8gkw'), so
                        CiteTuple(source, identifier).citekey() is just an
                        alternative constructor for CiteKey.

       Example:

       assert CiteTuple(source='doi', identifier='10/gf8gkw') == \
           CiteKey(value='doi:10/gf8gkw')
       """
    source: str
    identifier: str

    def citekey(self):
        return CiteKey(str(self))


class CSL_Dict(dict):
    def __init__(self, incoming_dict: dict):
        super().__init__(incoming_dict)

    def set_id(self, x):
        self['id'] = x
        return self

    @staticmethod
    def add_note(x):
        return x

    @staticmethod
    def generate_id(x):
        """If no id, make a hash"""
        return x

    @staticmethod
    def fix_type(x):
        return x

    @staticmethod
    def prune(self, x):
        return x

    def minimal(self):
        keys = ('title author URL issued type container-title'
                'volume issue page DOI').split()
        return CSL_Dict({k: v for k, v in self.items() if k in keys})

    def clean(self, prune=True):
        csl_item = self
        # csl_item.fix_type()
        # csl_item.add_note()
        # csl_item.generate_id()
        # if prune:
        #    csl_item.prune()
        return csl_item


@dataclass
class Handle:
    identifier: str

    def canonic(self):
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
    def canonic(self):
        from isbnlib import to_isbn13
        self.identifier = to_isbn13(self.identifier)
        return self


class DOI(Handle):
    def csl_dict(self):
        from manubot.cite.doi import get_doi_csl_item
        return CSL_Dict(get_doi_csl_item(self.identifier))

    def canonic(self):
        from manubot.cite.doi import expand_short_doi
        if self.identifier.startswith('10/'):
            self.identifier = expand_short_doi(self.identifier)
        return self


def standardize_citekey(citekey: str) -> str:
    return CiteKey(citekey).handle().canonic().citekey().str()


def citekey_to_csl_item(citekey: str, prune=True) -> dict:
    """
    Generate a CSL item with bibliographic information for *citekey* string.
    """
    return CiteKey(citekey).handle().canonic().csl_dict().clean()

"""
This is a study of core functionality of 'manubot cite'.

https://github.com/manubot/manubot/blob/master/manubot/cite

Simplifications:

  - just DOI citekey
  - rough cleaning of csl_item - few fields used, see minimal()
  - no additions of user-defined csl items
  - no csl style for output
  - not output format

Things learned - CSL related:

  - CSL output of Crossref is too dirty for pandoc citeproc, must be
    cleaned out
  - pandoc-citeproc needs id's to generate bibliography list, even with
    'nocite': '@*'
  - Uspekhi Fizicheskih Nauk has articles from first issue in 1918 online!
    with DOI references!

Things learned - other implementation:

  - requests_cache.install_cache() is an option for requests caching,
    optimal expiration period of cache to be decided, maybe should be in days
  - console encoding can matter for python subprocess.run(), eg it is 866
    for Windows in Russia locale
  - UserDict() is not JSON-serialisable with json.dump()

To explore:

  - convert asserts to unit tests + how to test on Windows? Github actions?
  - appling a particular csl style to bibliography
  - docopt for command line interface?
  - original suggestion for --from-file flag as in https://github.com/manubot/manubot/issues/135
  - maybe all three of '--from-file, stdin, or an argparse hack'

Target usecase:

   - a user keeps a list of searchable references in references.txt (doi, pmid, isbn, etc)
   - a user keeps a list of manual (not searchable) references as a YAML (or JSON) file in references-manual.txt
   - a user can produce a bibliography list with manubot cite in different formats


"""
import sys
import platform
from datetime import timedelta
from dataclasses import dataclass
from typing import List
import re
import json
import subprocess
import logging

import requests
import requests_cache

__VERSION__ = '0.2.3'

requests_cache.install_cache(expire_after=timedelta(hours=1))


def version():
    return __VERSION__


def get_manubot_user_agent():
    """
    Return a User-Agent string for web request headers to help services
    identify requests as coming from Manubot.
    """
    contact_email = 'contact@manubot.org'
    return (
        f'manubot/{version()} '
        f'({platform.system()}; Python/{sys.version_info.major}.{sys.version_info.minor}) '
        f'<{contact_email}>')


def server_response(url, header, user_agent=get_manubot_user_agent()):
    if user_agent:
        header['User-Agent'] = get_manubot_user_agent()
    response = requests.get(url, headers=header)
    try:
        return response.json()
    except Exception as error:
        logging.error(['Invalid response', response.url, response.text])
        raise error


@dataclass
class CiteKey:
    source: str
    identifier: str

    def citation(self):
        lookup = dict(doi=DOI, isbn=ISBN, pmid=PMID, arxiv=Arxiv)  # incomplete
        return lookup[self.source](self.identifier)


CITEKEY_PATTERN = re.compile(
    r'(?<!\w)@([a-zA-Z0-9][\w:.#$%&\-+?<>~/]*[a-zA-Z0-9/])')

CITEKEY_PATTERN2 = re.compile(
    r'(?<!\w)([a-zA-Z0-9][\w:.#$%&\-+?<>~/]*[a-zA-Z0-9/])')


def extract_citekeys(text: str):
    citekeys_strings = CITEKEY_PATTERN.findall(text)
    return [CiteKey(*s.split(':', 1)) for s in citekeys_strings]


def extract_citekeys_without_at(text: str):
    citekeys_strings = CITEKEY_PATTERN2.findall(text)
    return [CiteKey(*s.split(':', 1)) for s in citekeys_strings][0]


regexes = {
    'pmid': re.compile(r'[1-9][0-9]{0,7}'),
    'pmcid': re.compile(r'PMC[0-9]+'),
    'doi': re.compile(r'10\.[0-9]{4,9}/\S+'),
    'shortdoi': re.compile(r'10/[a-zA-Z0-9]+'),
    'wikidata': re.compile(r'Q[0-9]+'),
}


@dataclass
class Citation:
    identifier: str

    def normalise(self):
        return self

    def response(self):
        raise NotImplementedError

    def retrieve(self):
        raise NotImplementedError


class DOI(Citation):
    @property
    def url(self):
        return 'https://doi.org/{}'.format(self.identifier)

    def response(self):
        header = {'Accept': 'application/vnd.citationstyles.csl+json'}
        return server_response(self.url, header)

    def retrieve(self):
        csl_dict = self.response()
        csl_dict['URL'] = self.url
        return CiteItem(csl_dict)


class ISBN(Citation):
    pass


class PMID(Citation):
    pass


class Arxiv(Citation):
    pass


class Wikidata(Citation):
    pass


class CiteItem(dict):
    def __init__(self, incoming_dict):
        super().__init__(incoming_dict)

    def minimal(self):
        keys = 'title author URL issued type container-title volume issue page DOI'.split()
        new_dict = {k: v for k, v in self.items() if k in keys}
        return CiteItem(new_dict)


def add_missing_ids(csl_list):
    for i, item in enumerate(csl_list):
        try:
            item['id']
        except KeyError:
            item['id'] = 'id' + str(i)
            csl_list[i] = item
    return csl_list


def to_metadata(csl_list: List[CiteItem], csl_style: str) -> str:
    pandoc_metadata = {
        'nocite': '@*',
        'references': csl_list,
    }
    if csl_style:
        pandoc_metadata['csl'] = csl_style
    yaml = json.dumps(pandoc_metadata, ensure_ascii=False, indent=2)
    return f'---\n{yaml}\n...\n'


def call_pandoc_help():
    args = [
        'pandoc',
        '--help',
    ]
    result = subprocess.run(args, shell=True, capture_output=True)
    return result.stdout.decode('cp866')


def call_pandoc(input_str: str):
    args = [
        'pandoc',
        '--filter', 'pandoc-citeproc',
        '--to', 'plain', '--wrap', 'none'
    ]
    return subprocess.run(args,
                          input=input_str.encode(),
                          capture_output=True)


def bibliography(csl_list: List[CiteItem], csl_style=None) -> str:
    try:
        csl_list[0]
    except (TypeError, IndexError):
        csl_list = [csl_list]
    csl_list = add_missing_ids([ci.minimal() for ci in csl_list])
    input_str = to_metadata(csl_list, csl_style)
    output = call_pandoc(input_str)
    if output.returncode == 0:
        message = output.stdout
    else:
        message = output.stderr
    return message.decode()


def make_csl_list(citekeys: List[CiteKey]) -> List[CiteItem]:
    csl_list = []
    for citekey in citekeys:
        csl_item = citekey.citation() \
            .normalise() \
            .retrieve() \
            .minimal()
        csl_list.append(csl_item)
    return csl_list


def from_manuscript(text: str, csl_style=None, output_format='plain'):
    """Return bibliography list form text with @citekeys."""
    citekeys = extract_citekeys(text)
    csl_list = make_csl_list(citekeys)
    return bibliography(csl_list, csl_style)


def from_listing(text: str, csl_style=None, output_format='plain'):
    """Return bibliography list based on text with a citekey per line
       wihtout @.
    """
    citekeys = [extract_citekeys_without_at(
        x.strip()) for x in text.split("\n")]
    csl_list = make_csl_list(citekeys)
    return bibliography(csl_list, csl_style)


if __name__ == '__main__':
    d1 = DOI('10.1038/171737a0')  # Watson Crick on DNA
    d2 = DOI('10/ccg94v')  # Kary Mullis on PCR
    csl_list = [d.retrieve() for d in [d1, d2]]
    output = bibliography(csl_list, csl_style=None)
    print(output)

    text1 = "[@doi:10.1038/171737a0], [@doi:10/ccg94v]"
    output1 = from_manuscript(text1, csl_style=None)
    assert output == output1

    text2 = """doi:10.1038/171737a0
    doi:10/ccg94v"""
    output2 = from_listing(text2, csl_style=None)
    assert output == output2

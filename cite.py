""" 
This is a study of core functionality of 'manubot cite'.

https://github.com/manubot/manubot/blob/master/manubot/cite
"""

from datetime import timedelta
from dataclasses import dataclass
import json
import subprocess
import logging

import requests
import requests_cache

requests_cache.install_cache(expire_after=timedelta(hours=1))

def get_manubot_user_agent():
    """
    Return a User-Agent string for web request headers to help services
    identify requests as coming from Manubot.
    """
    import sys
    import platform
    contact_email = 'contact@manubot.org'
    try:
        from manubot import __version__ as manubot_version
    except ImportError:
        manubot_version = ''
    return (
        f'manubot/{manubot_version} '
        f'({platform.system()}; Python/{sys.version_info.major}.{sys.version_info.minor}) '
        f'<{contact_email}>'
    )


@dataclass
class Citation:
    identifier: str

    def retrieve(self):
        pass


class DOI(Citation):    
    @property
    def url(self):
        return 'https://doi.org/{}'.format(self.identifier)

    @staticmethod 
    def _response(url):
        header = {
            'Accept': 'application/vnd.citationstyles.csl+json',
            'User-Agent': get_manubot_user_agent(),
        }
        response = requests.get(url, headers=header)
        try:
            return response.json()
        except Exception as error:
            logging.error(['Invalid response', response.url, response.text])
            raise error
    
    def retrieve(self):
        csl_dict = self._response(self.url)
        csl_dict['URL'] = self.url
        return CitationItem(csl_dict)


class CitationItem(dict):
    def __init__(self, incoming_dict):
        super().__init__(incoming_dict)

    
def minimal(item: CitationItem):
   keys = 'title author URL issued type container-title volume issue page DOI'.split()
   new_dict = {k:v for k,v in item.items() if k in keys}
   return CitationItem(new_dict)


def add_missing_ids(csl_list):
    for i, item in enumerate(csl_list):
        try:
            item['id']
        except KeyError:
            item['id'] = 'id' + str(i)
            csl_list[i] = item
    return csl_list                   
  
    
def to_metadata(csl_list, csl_style=None):
    pandoc_metadata = {
        'nocite': '@*',
        'references': csl_list,
    }    
    if csl_style:
        pandoc_metadata['csl'] = csl_style
    return '---\n{yaml}\n...\n'.format(
        yaml=json.dumps(pandoc_metadata, ensure_ascii=False, indent=2)
    )


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


d1 = DOI('10.18632/aging.101684') 
d2 = DOI('10.3982/ECTA14673')
d3 = DOI('10.1017/aae.2017.13')
d4 = DOI('10.1038/171737a0')
d5 = DOI('10.3367/UFNr.0001.191801k.0077')


ci1, ci2, ci3, ci4, ci5 = [d.retrieve() for d in [d1, d2, d3, d4, d5]]


assert ci1['title'] == ('DNA methylation GrimAge strongly predicts '
                        'lifespan and healthspan')
assert ci2['title'] == 'Preferences for Truth‐Telling'
assert ci3['title'] == ('RESEARCH, PRODUCTIVITY, AND OUTPUT GROWTH '
                        'IN U.S. AGRICULTURE')
assert ci4['container-title'] == 'Nature'
# God, this is so cool: 1918 Uspekhi Fizicheskih Nauk article!
assert ci5['title'] == ('Изслѣдованiя и опредѣленiя длинъ волнъ въ красной '
                        'и инфра-красной области спектра')


csl_list1 = [minimal(ci) for ci in [ci1, ci2, ci3, ci4, ci5]]
assert to_metadata(csl_list1).startswith("---")
assert to_metadata(csl_list1).endswith("...\n")
  

input_str1=to_metadata(add_missing_ids(csl_list1))
k = call_pandoc(input_str1)
assert k.stderr.decode() == ''
assert k.stdout.decode().replace('\r\n', '\n') == \
"""Abeler, Johannes, Daniele Nosenzo, and Collin Raymond. 2019. “Preferences for Truth‐Telling.” _Econometrica_ 87 (4): 1115–53. https://doi.org/10.3982/ecta14673.

FUGLIE, KEITH, MATTHEW CLANCY, PAUL HEISEY, and JAMES MACDONALD. 2017. “RESEARCH, PRODUCTIVITY, AND OUTPUT GROWTH IN U.S. AGRICULTURE.” _Journal of Agricultural and Applied Economics_ 49 (4): 514–54. https://doi.org/10.1017/aae.2017.13.

Lu, Ake T., Austin Quach, James G. Wilson, Alex P. Reiner, Abraham Aviv, Kenneth Raj, Lifang Hou, et al. 2019. “DNA Methylation GrimAge Strongly Predicts Lifespan and Healthspan.” _Aging_ 11 (2): 303–27. https://doi.org/10.18632/aging.101684.

Vavilov, S.I. 1918. “Изслѣдованiя и опредѣленiя длинъ волнъ въ красной и инфра-красной области спектра.” _Uspekhi Fizicheskih Nauk_ 1 (1): 77–77. https://doi.org/10.3367/ufnr.0001.191801k.0077.

WATSON, J. D., and F. H. C. CRICK. 1953. “Molecular Structure of Nucleic Acids: A Structure for Deoxyribose Nucleic Acid.” _Nature_ 171 (4356): 737–38. https://doi.org/10.1038/171737a0.
"""

meta1 = """
---
nocite: |
  @*
references:
- type: article-journal
  id: WatsonCrick1953
  author:
  - family: Watson
    given: J. D.
  - family: Crick
    given: F. H. C.
  issued:
    date-parts:
    - - 1953
      - 4
      - 25
  title: 'Molecular structure of nucleic acids: a structure for deoxyribose
    nucleic acid'
  title-short: Molecular structure of nucleic acids
  container-title: Nature
  volume: 171
  issue: 4356
  page: 737-738
  DOI: 10.1038/171737a0
  URL: http://www.nature.com/nature/journal/v171/n4356/abs/171737a0.html
  language: en-GB
...
"""

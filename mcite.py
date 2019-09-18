"""
This is a study of core functionality of 'manubot cite'.

https://github.com/manubot/manubot/blob/master/manubot/cite

Simplifications:

  - just DOI citekey
  - rough cleaning of csl_item - few fields used, see minimal()
  - no additions of user-defined csl items
  - no csl style for output
  - no --output, just writing to stdout (will not produce MS Word) 


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
    for Windows in Russia locale, but pandoc output is always
    utf-8 for stdout. https://pandoc.org/MANUAL.html#character-encoding
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
from dataclasses import dataclass
from typing import List
import re
import json
import subprocess
import logging
from docopt import docopt

from citekey import accept
from server import server_response

CITEKEY_PATTERN = re.compile(
    r'(?<!\w)@([a-zA-Z0-9][\w:.#$%&\-+?<>~/]*[a-zA-Z0-9/])')

CITEKEY_PATTERN2 = re.compile(
    r'(?<!\w)([a-zA-Z0-9][\w:.#$%&\-+?<>~/]*[a-zA-Z0-9/])')


def extract_citekeys(text: str):
    return [accept(s) for s in CITEKEY_PATTERN.findall(text)]

# FIXME:
def extract_citekeys_without_at(text: str):
    citekeys_strings = CITEKEY_PATTERN2.findall(text)
    return [accept(s) for s in citekeys_strings][0]


regexes = {
    'pmid': re.compile(r'[1-9][0-9]{0,7}'),
    'pmcid': re.compile(r'PMC[0-9]+'),
    'doi': re.compile(r'10\.[0-9]{4,9}/\S+'),
    'shortdoi': re.compile(r'10/[a-zA-Z0-9]+'),
    'wikidata': re.compile(r'Q[0-9]+'),
}



class CiteItem(dict):
    def __init__(self, incoming_dict):
        super().__init__(incoming_dict)




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
    return result.stdout.decode()


arg_converter = dict(markdown=['--to', 'markdown_strict', '--wrap', 'none'],
                     jats=['--to', 'jats', '--standalone'],
                     docx=['--to', 'docx'],
                     html=['--to', 'html'],
                     plain=['--to', 'plain', '--wrap', 'none'])

def is_valid_format(output_format):
    return output_format and (output_format.lower() in arg_converter.keys())

def call_pandoc(input_str: str, output_format='plain'):
    args = [
        'pandoc',
        '--filter', 'pandoc-citeproc']
    args.extend(arg_converter[output_format])    
    return subprocess.run(args,
                          input=input_str.encode(),
                          capture_output=True)


def bibliography(csl_list: List[CiteItem], csl_style=None) -> str:
    if not isinstance(csl_list, list): 
       raise TypeError(csl_list)
    csl_list = add_missing_ids([ci.minimal() for ci in csl_list])
    input_str = to_metadata(csl_list, csl_style)
    output = call_pandoc(input_str)
    if output.returncode == 0:
        message = output.stdout
    else:
        message = output.stderr
    return message.decode()


def citekey_to_csl_item(citekey: CiteKey) -> CiteItem:
    return citekey.citation() \
            .normalise() \
            .retrieve() \
            .minimal() 

def text_to_citekeys(text: str):
    # What kind of input are we processing?
    # One with @citekeys - a manusript 
    if not text:
        return []
    if '@' in text or ('[' in text and ']' in text):
        return extract_citekeys(text)
    # A citekey by line - a listing of references
    else:
        xs = text.split("\n")
        return [extract_citekeys_without_at(x.strip()) for x in xs] # FIXME    

def make_csl_list(citekeys):
    return [citekey_to_csl_item(x) for x in citekeys]

def main(citekeys, csl_style=None, output_format='plain'):
    """Return bibliography list form text with @citekeys."""
    csl_list = make_csl_list(citekeys)
    return bibliography(csl_list, csl_style)

def as_json(csl_list):
    return json.dumps(csl_list, ensure_ascii=False, indent=2)    
    
if __name__ == '__main__':    
    args = docopt(
"""
Usage: mcite.py [--from-file FILE | ARGS...] [--render --format FORMAT] [--debug-args]
""")
    if args['FILE']:
        text = open(args['FILE']).read()
        citekeys = text_to_citekeys(text)
    elif args['ARGS']:
        citekeys = [extract_one_citekey(arg) for arg in args['ARGS']]
    elif not args['FILE'] and not args['ARGS']:
        text = sys.stdin.read()
        citekeys = text_to_citekeys(text)
    if args['--debug-args']:     
        for ci in citekeys:
            print(ci)            
        sys.exit(0)
    if args['--render']:
        fmt = args['--format']    
        output_format = fmt if is_valid_format(fmt) else 'plain'        
        print(main(citekeys, 
                   csl_style=None, 
                   output_format=output_format))
    else:
        print(as_json(make_csl_list(citekeys)))
        

"""
D:\github\manubot-cite-minimal (master)
λ python mcite.py --debug-args < ref.txt
['doi:10.1038/171737a0', 'doi:10/ccg94v']

D:\github\manubot-cite-minimal (master)
λ python mcite.py --debug-args doi:10.1038/171737a0 doi:10/ccg94v
['doi:10.1038/171737a0', 'doi:10/ccg94v']

D:\github\manubot-cite-minimal (master)
λ cat ref.txt | python mcite.py --debug-args
['doi:10.1038/171737a0', 'doi:10/ccg94v']

D:\github\manubot-cite-minimal (master)
λ python mcite.py --from-file ref.txt --debug-args
['doi:10.1038/171737a0', 'doi:10/ccg94v']
"""  

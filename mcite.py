"""
This is an implementation of manubot cite using classes and docopt.

https://github.com/manubot/manubot/blob/master/manubot/cite

Simplifications:

  - just DOI citekey
  - rough cleaning of csl_item - few fields used, see .minimal() method
  - no additions of user-defined csl items
  - no csl style for output (gost may be wanted)
  - no --output, just writing to stdout (will not produce MS Word)

Target usecase:

  - a user keeps a list of searchable references in references.txt (doi, pmid, isbn, etc)
  - a user keeps a list of manual (not searchable) references as a YAML (or JSON) file in references-manual.txt
  - a user can produce a bibliography list with manubot cite in different formats


To explore:

  - try Github actions
  - appling a particular csl style to bibliography
  - how to test on Windows

Done:
  - docopt for command line interface
  - convert asserts to unit tests
  - original suggestion for --from-file flag as in https://github.com/manubot/manubot/issues/135
  - all three of '--from-file, stdin, or an argparse hack'

"""
import sys
from typing import List
import json
import subprocess

from docopt import docopt

from citekey import CiteKey, Handle, CSL_Dict
from citekey import citekey_to_csl_item
from reader import text_to_citekey_strings


def start_caching(**kwargs):
    from datetime import timedelta
    import requests_cache
    if not kwargs:
        kwargs = dict(hours=1)
    live_period = timedelta(**kwargs)
    requests_cache.install_cache(expire_after=live_period)


start_caching()  # TODO: use config or cli option


def to_metadata(csl_list: List[CSL_Dict], csl_style: str) -> str:
    pandoc_metadata = {
        'nocite': '@*',
        'references': csl_list,
    }
    if csl_style:
        pandoc_metadata['csl'] = csl_style
    yaml = json.dumps(pandoc_metadata, ensure_ascii=False, indent=2)
    return f'---\n{yaml}\n...\n'


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


def call_pandoc_help():
    args = [
        'pandoc',
        '--help',
    ]
    result = subprocess.run(args, shell=True, capture_output=True)
    return result.stdout.decode()


def add_missing_ids(csl_list):  # will be replaced by .generate_id()
    for i, item in enumerate(csl_list):
        try:
            item['id']
        except KeyError:
            item['id'] = 'id' + str(i)
            csl_list[i] = item
    return csl_list


def make_csl_list(handles):
    csl_list = [handle.canonic().csl_dict().clean().minimal() for handle in handles]
    return add_missing_ids(csl_list)

def bibliography(handles: List[Handle], csl_style=None) -> str:
    csl_list = make_csl_list(handles)
    return bibliography_csl(csl_list, csl_style)


def bibliography_csl(csl_list: List[CSL_Dict], csl_style):
    input_str = to_metadata(csl_list, csl_style)
    output = call_pandoc(input_str)
    if output.returncode == 0:
        message = output.stdout
    else:
        message = output.stderr
    return message.decode()


def process_text_to_bibliography(text, csl_style=None, output_format='plain'):
    citekeys = text_to_citekey_strings(text)
    return main(citekeys, csl_style, output_format)


def main(citekey_strings, csl_style=None, output_format='plain'):
    """
    Return bibliography list form text with @citekeys or citekeys without @.
    """
    handles = [CiteKey(c).handle() for c in citekey_strings]
    return bibliography(handles, csl_style)


def as_json(csl_list):
    return json.dumps(csl_list, ensure_ascii=False, indent=2)


def make_json(citekey_strings):
    return as_json([citekey_to_csl_item(x) for x in citekey_strings])


if __name__ == '__main__':
    args = docopt("""
    Usage: mcite.py [--from-file FILE | ARGS...] [--render --format FORMAT] [--debug-args]
    """)
    if args['FILE']:
        text = open(args['FILE']).read()
        citekey_strings = text_to_citekey_strings(text)
    elif args['ARGS']:
        citekey_strings = args['ARGS']
    elif not args['FILE'] and not args['ARGS']:
        text = sys.stdin.read()
        citekey_strings = text_to_citekey_strings(text)
    if args['--debug-args']:
        for cs in citekey_strings:
            print(cs)
        sys.exit(0)
    if args['--render']:
        fmt = args['FORMAT']
        output_format = fmt if is_valid_format(fmt) else 'plain'
        output = main(citekey_strings,
                      csl_style=None,
                      output_format=output_format)
    else:
        output = make_json(citekey_strings)
    print(output)

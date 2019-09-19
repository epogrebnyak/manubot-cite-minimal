import re

CITEKEY_PATTERN = re.compile(
    r'(?<!\w)@([a-zA-Z0-9][\w:.#$%&\-+?<>~/]*[a-zA-Z0-9/])')

CITEKEY_PATTERN2 = re.compile(
    r'(?<!\w)([a-zA-Z0-9][\w:.#$%&\-+?<>~/]*[a-zA-Z0-9/])')


def extract_citekeys(text: str):
    return [s for s in CITEKEY_PATTERN.findall(text)]

# FIXME:


def extract_citekeys_without_at(text: str):
    citekeys_strings = CITEKEY_PATTERN2.findall(text)
    return [s for s in citekeys_strings][0]


def text_to_citekey_strings(text: str):
    if not text:
        return []
    # What kind of input are we processing?
    if '@' in text:
        # One with @citekeys - a manusript
        return extract_citekeys(text)
    else:
        # A citekey by line - a listing of references
        xs = [x.strip() for x in text.split("\n")]
        return [extract_citekeys_without_at(x.strip()) for x in xs]


regexes = {
    'pmid': re.compile(r'[1-9][0-9]{0,7}'),
    'pmcid': re.compile(r'PMC[0-9]+'),
    'doi': re.compile(r'10\.[0-9]{4,9}/\S+'),
    'shortdoi': re.compile(r'10/[a-zA-Z0-9]+'),
    'wikidata': re.compile(r'Q[0-9]+'),
}

import re

CITEKEY_PATTERN = re.compile(
    r'(?<!\w)@([a-zA-Z0-9][\w:.#$%&\-+?<>~/]*[a-zA-Z0-9/])')


def extract_citekeys(text: str):
    """Requires @ for citation."""
    return [s for s in CITEKEY_PATTERN.findall(text)]


def extract_citekeys_by_line(text: str):
    result = []
    for line in text.split('\n'):
        line.strip()
        # very permissive - allow everything with a colon to be evaluated
        if ':' in line:
            result.append(line)
    return result        


def text_to_citekey_strings(text: str):
    if not text:
        return []
    # What kind of input are we processing?
    if '@' in text:
        # Input with @citekeys - a manusript
        return extract_citekeys(text)
    else:
        # A citekey by line - a listing of references        
        return extract_citekeys_by_line(text)


regexes = {
    'pmid': re.compile(r'[1-9][0-9]{0,7}'),
    'pmcid': re.compile(r'PMC[0-9]+'),
    'doi': re.compile(r'10\.[0-9]{4,9}/\S+'),
    'shortdoi': re.compile(r'10/[a-zA-Z0-9]+'),
    'wikidata': re.compile(r'Q[0-9]+'),
}

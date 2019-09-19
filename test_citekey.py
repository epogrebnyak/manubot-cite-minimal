from citekey import citekey_to_csl_item, standardize_citekey
from citekey import CiteKey, DOI


import random
doi = random.choice(['doi:10.1038/171737a0', 'doi:10/ccg94v'])


def test_pipeline():
    ci = CiteKey('doi:10.1038/171737a0').handle().csl_dict()
    assert ci['title'].startswith('Molecular Structure of Nucleic Acids')


def test_standardize_citekey():
    expected = 'doi:10.1016/s0933-3657(96)00367-3'
    assert standardize_citekey('doi:10/b6vnmd') == expected
    assert standardize_citekey('doi:10/B6VNMD') == expected


def test_citekey_to_csl_item():
    ci = citekey_to_csl_item('doi:10/b6vnmd')
    assert ci['title'].startswith('An evaluation of machine-learning methods')
    assert ci['DOI'] == '10.1016/s0933-3657(96)00367-3'


def test_doi_canonic():
    target = DOI('10.1016/s0933-3657(96)00367-3')
    assert DOI('10/b6vnmd').canonic() == target
    assert DOI('10/B6VNMD').canonic() == target


def test_1():
    ci = CiteKey('doi:10.1038/171737a0').handle().csl_dict()
    assert ci['title'].startswith('Molecular Structure of Nucleic Acids')
    assert standardize_citekey(
        'doi:10/gf8gkw') == 'doi:10.1038/d41586-019-02781-4'
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

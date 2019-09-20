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
    assert citekey_to_csl_item('doi:10/gf8gkw').minimal() == {'issue': '7774',
 'DOI': '10.1038/d41586-019-02781-4',
 'type': 'article-journal',
 'page': '310-310',
 'title': 'How to make computing more sustainable',
 'issued': {'date-parts': [[2019, 9]]},
 'URL': 'https://doi.org/gf8gkw'}
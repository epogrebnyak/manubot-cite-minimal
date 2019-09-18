from citekey import citekey_to_csl_item, standardize_citekey, accept
from citekey import CiteKey, DOI, ShortDOI


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
    assert ci['title'] == 'An evaluation of machine-learning methods for predicting pneumonia mortality'
    assert ci['DOI'] == '10.1016/s0933-3657(96)00367-3'

def test_short_doi_standardize():
    target = DOI('10.1016/s0933-3657(96)00367-3')
    assert ShortDOI('10/b6vnmd').standardize() == target
    assert ShortDOI('10/B6VNMD').standardize() == target        
    
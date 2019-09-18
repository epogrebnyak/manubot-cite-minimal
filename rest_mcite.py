from mcite import (DOI, to_metadata, bibliography, text_to_citekeys,
                   add_missing_ids, call_pandoc)

def test_ouputs():
    d1 = DOI('10.1038/171737a0')  # Watson Crick on DNA
    d2 = DOI('10/ccg94v')  # Kary Mullis on PCR
    csl_list = [d.retrieve() for d in [d1, d2]]
    output = bibliography(csl_list, csl_style=None)
    print(output)

    text1 = "[@doi:10.1038/171737a0], [@doi:10/ccg94v]"
    output1 = text_to_citekeys(text1, csl_style=None)
    assert output == output1

    text2 = """doi:10.1038/171737a0
    doi:10/ccg94v"""
    output2 = text_to_citekeys(text2, csl_style=None)
    assert output == output2


def test_doi_1(): # not run
    csl_item = DOI('10.7287/peerj.preprints.3100v1').csl_item()
    #assert csl_item['id'] == '11cb5HXoY'
    assert csl_item['URL'] == 'https://doi.org/10.7287/peerj.preprints.3100v1'
    assert csl_item['DOI'] == '10.7287/peerj.preprints.3100v1'
    assert csl_item['type'] == 'report'
    assert csl_item['title'] == 'Sci-Hub provides access to nearly all scholarly literature'
    authors = csl_item['author']
    assert authors[0]['family'] == 'Himmelstein'
    assert authors[-1]['family'] == 'Greene'

def test_doi_2(): # not run    
    d1 = DOI('10.18632/aging.101684')
    d2 = DOI('10.3982/ECTA14673')
    d3 = DOI('10.1017/aae.2017.13')
    d4 = DOI('10.1038/171737a0')
    d5 = DOI('10.3367/UFNr.0001.191801k.0077')

    ci1, ci2, ci3, ci4, ci5 = [d.csl_item() for d in [d1, d2, d3, d4, d5]]

    assert ci1['title'] == ('DNA methylation GrimAge strongly predicts '
                            'lifespan and healthspan')
    assert ci2['title'] == 'Preferences for Truth‐Telling'
    assert ci3['title'] == ('RESEARCH, PRODUCTIVITY, AND OUTPUT GROWTH '
                            'IN U.S. AGRICULTURE')
    assert ci4['container-title'] == 'Nature'
    # God, this is so cool: 1918 Uspekhi Fizicheskih Nauk article!
    assert ci5['title'] == (
        'Изслѣдованiя и опредѣленiя длинъ волнъ въ красной '
        'и инфра-красной области спектра')

    csl_list1 = [ci.minimal() for ci in [ci1, ci2, ci3, ci4, ci5]]
    assert to_metadata(csl_list1, csl_style=None).startswith("---")
    assert to_metadata(csl_list1, csl_style=None).endswith("...\n")

    input_str1 = to_metadata(add_missing_ids(csl_list1), csl_style=None)
    k = call_pandoc(input_str1)
    assert k.stderr.decode() == ''
    assert k.stdout.decode().replace(
        '\r\n',
        '\n') == """Abeler, Johannes, Daniele Nosenzo, and Collin Raymond. 2019. “Preferences for Truth‐Telling.” _Econometrica_ 87 (4): 1115–53. https://doi.org/10.3982/ecta14673.

FUGLIE, KEITH, MATTHEW CLANCY, PAUL HEISEY, and JAMES MACDONALD. 2017. “RESEARCH, PRODUCTIVITY, AND OUTPUT GROWTH IN U.S. AGRICULTURE.” _Journal of Agricultural and Applied Economics_ 49 (4): 514–54. https://doi.org/10.1017/aae.2017.13.

Lu, Ake T., Austin Quach, James G. Wilson, Alex P. Reiner, Abraham Aviv, Kenneth Raj, Lifang Hou, et al. 2019. “DNA Methylation GrimAge Strongly Predicts Lifespan and Healthspan.” _Aging_ 11 (2): 303–27. https://doi.org/10.18632/aging.101684.

Vavilov, S.I. 1918. “Изслѣдованiя и опредѣленiя длинъ волнъ въ красной и инфра-красной области спектра.” _Uspekhi Fizicheskih Nauk_ 1 (1): 77–77. https://doi.org/10.3367/ufnr.0001.191801k.0077.

WATSON, J. D., and F. H. C. CRICK. 1953. “Molecular Structure of Nucleic Acids: A Structure for Deoxyribose Nucleic Acid.” _Nature_ 171 (4356): 737–38. https://doi.org/10.1038/171737a0.
"""    
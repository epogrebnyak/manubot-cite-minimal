from mcite import (to_metadata, bibliography,
                   process_text_to_bibliography,
                   add_missing_ids, call_pandoc)
from citekey import DOI


def test_process_text_to_bibliography():
    d1 = DOI('10.1038/171737a0')  # Watson Crick on DNA
    d2 = DOI('10/ccg94v')         # Kary Mullis on PCR
    csl_list = [d.csl_dict() for d in [d1, d2]]
    output = bibliography(csl_list, csl_style=None)

    text1 = "[@doi:10.1038/171737a0], [@doi:10/ccg94v]"
    output1 = process_text_to_bibliography(text1, csl_style=None)
    assert output == output1

    text2 = """doi:10.1038/171737a0
    doi:10/ccg94v"""
    output2 = process_text_to_bibliography(text2, csl_style=None)
    assert output == output2


def test_doi_1():  # not run
    csl_item = DOI('10.7287/peerj.preprints.3100v1').csl_dict()
    assert csl_item['URL'] == 'https://doi.org/b9s6'
    assert csl_item['DOI'] == '10.7287/peerj.preprints.3100v1'
    assert csl_item['type'] == 'posted-content'
    assert csl_item['title'] == 'Sci-Hub provides access to nearly all scholarly literature'
    authors = csl_item['author']
    assert authors[0]['family'] == 'Himmelstein'
    assert authors[-1]['family'] == 'Greene'


def test_doi_2():  # not run
    d1 = DOI('10.18632/aging.101684')
    d2 = DOI('10.3982/ECTA14673')
    d3 = DOI('10.1017/aae.2017.13')
    d4 = DOI('10.1038/171737a0')
    d5 = DOI('10.3367/UFNr.0001.191801k.0077')

    ci1, ci2, ci3, ci4, ci5 = [d.csl_dict() for d in [d1, d2, d3, d4, d5]]

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
    assert k.stdout.decode() == 'Abeler, Johannes, Daniele Nosenzo, and Collin Raymond. 2019. “Preferences for Truth‐Telling,” no. 4: 1115–53. https://doi.org/10.3982/ecta14673.\r\n\r\nFUGLIE, KEITH, MATTHEW CLANCY, PAUL HEISEY, and JAMES MACDONALD. 2017. “RESEARCH, PRODUCTIVITY, AND OUTPUT GROWTH IN U.S. AGRICULTURE,” no. 4 (July): 514–54. https://doi.org/10.1017/aae.2017.13.\r\n\r\nLu, Ake T., Austin Quach, James G. Wilson, Alex P. Reiner, Abraham Aviv, Kenneth Raj, Lifang Hou, et al. 2019. “DNA Methylation GrimAge Strongly Predicts Lifespan and Healthspan,” no. 2 (January): 303–27. https://doi.org/10.18632/aging.101684.\r\n\r\nVavilov, S.I. 1918. “Изслѣдованiя и опредѣленiя длинъ волнъ въ красной и инфра-красной области спектра,” no. 1: 77–77. https://doi.org/10.3367/ufnr.0001.191801k.0077.\r\n\r\nWATSON, J. D., and F. H. C. CRICK. 1953. “Molecular Structure of Nucleic Acids: A Structure for Deoxyribose Nucleic Acid,” no. 4356 (April): 737–38. https://doi.org/10.1038/171737a0.\r\n'

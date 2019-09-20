from reader import text_to_citekey_strings

doc1 = """
doi:10.1038/171737a0
doi:10/ccg94v
"""

doc2 = """
@doi:10.1038/171737a0 [@doi:10/ccg94v]
"""

ref = ['doi:10.1038/171737a0', 'doi:10/ccg94v']

def test_text_to_citekey_strings_on_lined_input():
    assert text_to_citekey_strings(doc1) == ref 
   
def test_text_to_citekey_strings_on_at_input():
    assert text_to_citekey_strings(doc2) == ref 
    

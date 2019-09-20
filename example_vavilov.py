from mcite import bibliography
from citekey import DOI

d1 = DOI('10.3367/UFNr.0001.191801c.0025')
d2 = DOI('10.3367/UFNr.0001.191801d.0039') 
d3 = DOI('10.3367/UFNr.0001.191801k.0077')
bib = bibliography([d1, d2, d3])
print(bib)

"""
Lazarev, P.P. 1918. “Современныя задачи молекулярной физики,” no. 1: 25–38. https://doi.org/10.3367/ufnr.0001.191801c.0025.

Rakovskii, A.V. 1918. “Изслѣдованiя Бриджмена въ области высокихъ давленiй. I,” no. 1: 39–53. https://doi.org/10.3367/ufnr.0001.191801d.0039.

Vavilov, S.I. 1918. “Изслѣдованiя и опредѣленiя длинъ волнъ въ красной и инфра-красной области спектра,” no. 1: 77–77. https://doi.org/10.3367/ufnr.0001.191801k.0077.
"""
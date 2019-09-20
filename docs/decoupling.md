Good stuff:

- robust bibliographic queries
- extensive logging

Not as good - better change:

- parts of code not a own level of abstraction
- consequence - many `if-then`'s
- transformation pypeline not clear
- `assert` used for certian checks
- version with importable fucntions not released on pypi

Not as good - can live with it:

- rather tight coupling with rest of manubot package
- sometimes inconclusive logging or check results, clutter if logging level not set out
- some common parts in server calls code may extracted, but risks 406 error for example 

Subjective:

- argparse vs docopt
- important parts, not helper functions are in util.py 

View:

- `Handle` classes are at core of API: `DOI`, `ISBN`, etc.
- `bibliography` function works on a list of handles to produce
   CSL JSON or a formatted reference list with `pandoc-cite-proc`
- value added in `Handle` classes - work well to obtain bibliographic information    
- value added in `bibliography` - makes `pandoc-cite-proc` behave well for standalone bibliography list 
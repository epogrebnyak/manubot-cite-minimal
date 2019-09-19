Things learned - CSL related:

  - CSL output of Crossref is too dirty for pandoc citeproc, must be
    cleaned out
  - pandoc-citeproc needs id's to generate bibliography list, even with
    'nocite': '@*'
  - Uspekhi Fizicheskih Nauk has articles from first issue in 1918 online!
    with DOI references!

Things learned - other implementation:

  - requests_cache.install_cache() is an option for requests caching,
    optimal expiration period of cache to be decided, maybe should be in days
  - console encoding can matter for python subprocess.run(), eg it is 866
    for Windows in Russia locale, but pandoc output is always
    utf-8 for stdout. https://pandoc.org/MANUAL.html#character-encoding
  - UserDict() is not JSON-serialisable with json.dump()
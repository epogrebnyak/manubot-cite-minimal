"""
D:\github\manubot-cite-minimal (master)
λ python mcite.py --debug-args < ref.txt
['doi:10.1038/171737a0', 'doi:10/ccg94v']

D:\github\manubot-cite-minimal (master)
λ python mcite.py --debug-args doi:10.1038/171737a0 doi:10/ccg94v
['doi:10.1038/171737a0', 'doi:10/ccg94v']

D:\github\manubot-cite-minimal (master)
λ cat ref.txt | python mcite.py --debug-args
['doi:10.1038/171737a0', 'doi:10/ccg94v']

D:\github\manubot-cite-minimal (master)
λ python mcite.py --from-file ref.txt --debug-args
['doi:10.1038/171737a0', 'doi:10/ccg94v']
"""

"""
doi:10.1038/171737a0
doi:10/ccg94v
"""

import io
import subprocess

def test_cli():
    commands = [
      'python mcite.py --debug-args < ref.txt'
    , 'python mcite.py --debug-args doi:10.1038/171737a0 doi:10/ccg94v'
    , 'python mcite.py --from-file ref.txt --debug-args'
    , 'cat ref.txt | python mcite.py --debug-args'
    ]
    reference_output = ['doi:10.1038/171737a0', 'doi:10/ccg94v']
    for args in commands:
        result = subprocess.run(args, shell=True, capture_output=True)
        x = result.stdout.decode().split()
        x == reference_output


def test_cli_stdin(monkeypatch): #fails
    monkeypatch.setattr('sys.stdin', io.StringIO('doi:10.1038/171737a0 \r\n doi:10/ccg94v'))
    result = subprocess.run('python mcite.py', shell=True, capture_output=True)
    assert result.stdout.decode().split() == ['doi:10.1038/171737a0', 'doi:10/ccg94v']


# x = subprocess.run('python mcite.py', 
                   # stdin=io.StringIO('doi:10.1038/171737a0 \r\n doi:10/ccg94v'), 
                   # shell=True, 
                   # capture_output=True)


"""
λ python mcite.py
doi:10.1038/171737a0
doi:10/ccg94v
^Z
Traceback (most recent call last):
  File "mcite.py", line 154, in <module>
    citekey_strings = text_to_citekey_strings(text)
  File "D:\github\manubot-cite-minimal\reader.py", line 31, in text_to_citekey_strings
    return [extract_citekeys_without_at(x.strip()) for x in xs]
  File "D:\github\manubot-cite-minimal\reader.py", line 31, in <listcomp>
    return [extract_citekeys_without_at(x.strip()) for x in xs]
  File "D:\github\manubot-cite-minimal\reader.py", line 18, in extract_citekeys_without_at
    return [s for s in citekeys_strings][0]
IndexError: list index out of range    
"""
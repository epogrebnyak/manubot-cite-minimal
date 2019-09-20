import subprocess

# See also calls.bat for call options 

doc = """
doi:10.1038/171737a0
doi:10/ccg94v
"""

def test_cli():
    commands = [
        'python mcite.py --debug-args < ref.txt',
        'python mcite.py --debug-args doi:10.1038/171737a0 doi:10/ccg94v',
        'python mcite.py --from-file ref.txt --debug-args',
        'cat ref.txt | python mcite.py --debug-args']
    reference_output = ['doi:10.1038/171737a0', 'doi:10/ccg94v']
    for args in commands:
        result = subprocess.run(args, shell=True, capture_output=True)
        x = result.stdout.decode().split()
        x == reference_output


def test_cli_stdin():  
    out = subprocess.run('python mcite.py --debug-args', 
                         input=doc.encode(), 
                         shell=True, 
                         capture_output=True)
    assert out.stdout.decode().split() == ['doi:10.1038/171737a0', 'doi:10/ccg94v']

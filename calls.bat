echo doi:10.1038/171737a0 > ref.txt
echo doi:10/ccg94v >> ref.txt 

python mcite.py --debug-args < ref.txt
python mcite.py --debug-args doi:10.1038/171737a0 doi:10/ccg94v
python mcite.py --from-file ref.txt --debug-args
cat ref.txt | python mcite.py --debug-args
type ref.txt | python mcite.py --debug-args

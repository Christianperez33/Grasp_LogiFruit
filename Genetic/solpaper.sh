#!/bin/bash
start=`date +%s`

python3 ./main.py -i 100  -s  ./poolsol/ -ns 2
python3 ./main.py -i 100  -s  ./poolsol/ -ns 4
python3 ./main.py -i 200  -s  ./poolsol/ -ns 2
python3 ./main.py -i 200  -s  ./poolsol/ -ns 4

end=`date +%s`
runtime=$((end-start))
echo "Tiempo de ejecución: $runtime" 

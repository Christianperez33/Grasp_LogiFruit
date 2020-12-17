#!/bin/bash
# start=`date +%s`

for a in {2..10..2}
do
    echo -ne "Progress nsup: $[ $a*100/10 ]% \n";
    python3 ./main.py -i 200  -s  ./poolsol/ -ns $a -r 0
    python3 ./main.py -i 200  -s  ./poolsol/ -ns $a -r 1
done

# end=`date +%s`
# runtime=$((end-start))
# echo "Tiempo de ejecución: $runtime"

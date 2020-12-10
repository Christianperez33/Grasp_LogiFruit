#!/bin/bash
start=`date +%s`
for i in {1..5..1}
do
    for a in {50..100..10}
    do
        echo -ne "Progress Iter: $[ (100/5)*($i) ]% - Progress Alfa: $[ $a*100/100 ]% \n";
        python3 main.py -i $i -av $a  -m 2 -g True -t True -x ../data/StockSolucionResolver.csv -y ../data/viajes_zonas.xml --debug True
    done
done
end=`date +%s`
runtime=$((end-start))
echo "Tiempo de ejecución: $runtime"

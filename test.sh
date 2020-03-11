#!/bin/bash
start=`date +%s`
for i in {1..1..1}
do
    for a in {0..100..10}
    do
        echo -ne "Progress Iter: $[ (100/1)*($i) ]% - Progress Alfa: $[ $a*100/100 ]% \n";
        python main.py -i $i -av $a -b 90 -m 2 -s 12 -g True -t True -x ./data/StockSolucionResolver.csv -y ./data/viajes_zonas.xml --debug True
    done
done
end=`date +%s`
runtime=$((end-start))
echo "Tiempo de ejecución: $runtime"
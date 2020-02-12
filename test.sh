#!/bin/bash
start=`date +%s`
for i in {1..1..1}
do
    for a in {20..50..10}
    do
        echo -ne "Progress Iter: $[ $i*100/1 ]% - Progress Alfa: $[ $a*100/50 ]%";
        python3.6 main.py -i $i -av $a -g True -t True -x ./data/stock_4enero20.csv -y ./data/viajes_4enero20.xml --debug False
    done
done
end=`date +%s`
runtime=$((end-start))
echo "Tiempo de ejecución: $runtime"
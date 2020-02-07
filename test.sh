#!/bin/bash
for i in {1..5..1}
do
    for l in {2..15..1}
    do
        for a in {50..100..5}
        do
            echo -ne "Progress Iter: $[ $i*100/5 ]% - Progress LCR: $[ $l*100/15 ]% - Progress Alfa: $[ $a ]%\r";
            python3.6 main.py -i $i -l $l -av $a -g True -t True -x ./data/stock_4enero20.csv -y ./data/viajes_4enero20.xml --debug False
        done
    done
done
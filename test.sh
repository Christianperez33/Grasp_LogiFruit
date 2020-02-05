#!/bin/bash
for i in {1..10..1}
do
    for l in {2..15..1}
    do
        for a in {0..100..5}
        do
            python3.6 main.py -i $i -l $l -av $a -x ./data/stock_4enero20.csv -y ./data/viajes_4enero20.xml -g True 
        done
    done
done
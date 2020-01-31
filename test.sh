#!/bin/bash
for i in {80..100..5}
do
    python3.6 main.py --i 5 -l 5  -x ./data/stock_4enero20.csv -y ./data/viajes_4enero20.xml -g True -av $i
done
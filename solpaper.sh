#!/bin/bash
start=`date +%s`
# echo "GRASP"
# echo "DATOS DE 5JULIO"
# python3 main.py -i 1   -x ./Genetic/data_grasp/14JULIO/stock.csv  -y ./Genetic/data_grasp/14JULIO/viajes.xml
# python3 main.py -i 5   -x ./Genetic/data_grasp/14JULIO/stock.csv  -y ./Genetic/data_grasp/14JULIO/viajes.xml
# python3 main.py -i 10  -x ./Genetic/data_grasp/14JULIO/stock.csv  -y ./Genetic/data_grasp/14JULIO/viajes.xml
# python3 main.py -i 20  -x ./Genetic/data_grasp/14JULIO/stock.csv  -y ./Genetic/data_grasp/14JULIO/viajes.xml
# echo "DATOS DE 14JULIO"
# python3 main.py -i 1   -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml
# python3 main.py -i 5   -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml
# python3 main.py -i 10  -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml
# python3 main.py -i 20  -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml
# echo "GA"
echo "DATOS DE 5JULIO"
python3 ./Genetic/main.py -i 1   -x ./Genetic/data_grasp/5JULIO/stock.csv  -y ./Genetic/data_grasp/5JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/5JULIO/
python3 ./Genetic/main.py -i 5   -x ./Genetic/data_grasp/5JULIO/stock.csv  -y ./Genetic/data_grasp/5JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/5JULIO/
python3 ./Genetic/main.py -i 10  -x ./Genetic/data_grasp/5JULIO/stock.csv  -y ./Genetic/data_grasp/5JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/5JULIO/
python3 ./Genetic/main.py -i 20  -x ./Genetic/data_grasp/5JULIO/stock.csv  -y ./Genetic/data_grasp/5JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/5JULIO/
echo "DATOS DE 14JULIO"
python3 ./Genetic/main.py -i 1   -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/14JULIO/
python3 ./Genetic/main.py -i 5   -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/14JULIO/
python3 ./Genetic/main.py -i 10  -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/14JULIO/
python3 ./Genetic/main.py -i 20  -x ./Genetic/data_grasp/14JULIO/stock.csv -y ./Genetic/data_grasp/14JULIO/viajes.xml -s ./RESULTADOS_PAPER/IEEE/GRASPSOLS/14JULIO/

end=`date +%s`
runtime=$((end-start))
echo "Tiempo de ejecución: $runtime" 

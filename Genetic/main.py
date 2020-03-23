import time
from genetic import *
import argparse

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

argparser = argparse.ArgumentParser()
argparser.add_argument('-i', '--iter', help='numero de iteraciones del AG', default=1)
args = argparser.parse_args()
start_time = time.time()

g = Genetic()

x = develope(g,int(args.iter))
print(x)

print("--- {} seconds ---".format(time.time() - start_time))
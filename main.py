import time
from grasp import *

start_time = time.time()
sol = 0
val = 0

for i in range(5):
    g = Grasp()
    x = g.GRASP_Solution()
    if x[1] >= val :
        sol = x[0]
        val = x[1]
    print(x[1])
    

print("--- %s seconds ---" % (time.time() - start_time))

# f = open('result.csv','wb')
# w = csv.DictWriter(f,{}.keys())
# w.writerows({})
# f.close()
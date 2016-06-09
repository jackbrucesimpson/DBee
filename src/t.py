import threading
import time
from multiprocessing import Pool
from multiprocessing import Process

from beehaviour.database import query_db
from beehaviour.bee import Bee
from beehaviour.experiment import Experiment

experiment = Experiment(2)
bee_id_list = list(range(1000))

t0 = time.time()

bee_id_dict = experiment.retrieve_process_bees(bee_id_list)
print(bee_id_dict[0].cells_visited)

t1 = time.time()
print(t1-t0)

print('sleep!')
time.sleep(10)

t0 = time.time()

bee_id_dict = experiment.retrieve_process_bees(bee_id_list)
print(bee_id_dict[0].cells_visited)

t1 = time.time()
print(t1-t0)



'''
remaining_bee_ids = list(range(1000))

for i in range(0, len(remaining_bee_ids), 100):
    subset_bee_ids = remaining_bee_ids[i:i+100]
    print(subset_bee_ids)

    if subset_bee_ids[-1] != remaining_bee_ids[-1]:
        print('DONE!')
'''
'''

def f(anum):
    nn = 0 + anum
    for x in range(90000000):
        nn += x

    return(nn)

t0 = time.time()

pool = Pool(processes=8)

result = pool.map(f, list(range(8)))

cleaned = [x for x in result if not x is None]

pool.close()
pool.join()

print(cleaned)



t1 = time.time()
print(t1-t0)

def worker(num):
    """thread worker function"""
    time.sleep(2)
    print ('Worker:',num)
    return

threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()


# get initial bee
# parse through it while spawning thread to get the next bee [checking if they've reached the final bee]
# cell dictionary -> points

list_bee_ids = list(range(100))

pool = Pool(processes=4)

for i in range(1):

    t0 = time.time()
    #return_val = query_db(table='bee_coords, paths', cols=['paths.BeeID', 'bee_coords.PathID', 'bee_coords.Frame', 'bee_coords.X', 'bee_coords.Y'], where='bee_coords.PathID = paths.PathID', group_condition='AND BeeID IN', group_list=list_bee_ids, order='ORDER BY Frame ASC')
    #res = pool.apply_async(query_db, (), dict(table='bee_coords, paths', cols=['paths.BeeID', 'bee_coords.PathID', 'bee_coords.Frame', 'bee_coords.X', 'bee_coords.Y'], where='bee_coords.PathID = paths.PathID', group_condition='AND BeeID IN', group_list=list_bee_ids, order='ORDER BY Frame ASC')) # tuple of args for foo

    nn = 0
    for x in range(200000000):
        nn += x

    return_val = res.get()

    t1 = time.time()
    print(t1-t0, nn, return_val[0], '\n')


for bee_id in [1,2,3]:
    t0 = time.time()
    t = threading.Thread(target=worker, args=(1,))
    t.start()
    time.sleep(5)
    t1 = time.time()
    print(bee_id)
    print(t1-t0)
'''

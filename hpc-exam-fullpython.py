import numpy as np
import os
from mpi4py import MPI
import util as ut
import json
from datatypes import ResponseMessage
import threading

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
name = MPI.Get_processor_name()
info = MPI.INFO_ENV
service = 'hpc'
debug = False
path = '/nfs/'

def receive(comm,pn,stats,results,cols,resultsrows):
    data = None
    while data != "stop":
        try:
            data = json.loads(comm.recv(source=pn))
            stats.append(data)
            rowdata = ut.readMatrixFromFile(data["result"])
            row = int(data["row"])
            for j in range(cols):
                results[row*cols+j]=rowdata[j]
        except:
            break

def prod (vect,matr):
    cols = int(len(vect))
    rows = int(len(matr)/cols)
    res = np.zeros(rows, dtype=np.int32)
    for row in range (rows):
        r = 0
        for col in range (cols):
            r = r + vect[col] * matr [col * rows + row]
        res[row] = r
    return res

if rank == 0:

    ut.log("Starting main process")
    port = MPI.Open_port(info)
    ut.log("opened port: '%s'", port)
    MPI.Publish_name(service, info, port)
    ut.log("published service: '%s'", service)

    out = {"t":0,"results":None,"stats":None}
    
    threads = []
    global results
    global stats
    
    n,m,p,max=500,500,500,10

    results = []
    stats = []
    debug = True

    a = ut.initRandomMatrix('A',n,m,max,debug)
    b = ut.initRandomMatrix('B',m,p,max,debug)
    c = ut.initZeroMatrix('C',n,p,debug)

    for i in range(size-1):
        thread = threading.Thread(target=receive, args=(comm,i+1,stats,c,p,n,))
        thread.name="rank-"+str(i+1)+"-receiver"
        threads.append(thread)
        thread.start()
    
    t0 = ut.current_milli_time()
    outcsv = str(t0)+","+str(size)+","+str(n)+","+str(m)+","+str(p)
    filenameb = path+str(t0)+'-b.json'
    filenamec = path+str(t0)+'-c.json'
    filenames = path+str(t0)+'-stats.json'
    
    ut.writeMatrixToFile(b,filenameb)
    messages={}
    for i in range(size):
        messages[i]={
            "a":[],
            "b":None
        }

    for i in range(n):
        destproc = 1 + i % (size-1)
        filename = path+str(t0)+'-a-r'+str(i).zfill(5)+'-p'+str(destproc).zfill(2)+'.json'
        r = a.reshape(n, m)[i]
        ut.writeMatrixToFile(r,filename)
        messages[destproc]["a"].append(filename)
        messages[destproc]["b"] = filenameb
    
    t0 = ut.current_milli_time()
    comm.bcast(json.dumps(messages),0)
    for thread in threads:
        thread.join()
    out['t'] = ut.current_milli_time() - t0
    outcsv = outcsv + ',' + str(out['t']) + '\n'
    out['stats'] = stats
    out['results'] = results
    ut.writeMatrixToFile(c, filenamec)
    ut.writeStatsToFile(out, filenames)
    
    with open(path+"stats-fullpython.csv", "a") as myfile:
        myfile.write(outcsv)
        myfile.close()
else:
    port = None
    while port is None:
        try:
            port = MPI.Lookup_name(service)
        except:
            pass
    out = ResponseMessage(result=None, type=None, time=0, row=None)
    message = json.loads(comm.bcast(None,0))
    b = ut.readMatrixFromFile(message[str(rank)]['b'])
    for patha in message[str(rank)]['a']:
        a = ut.readMatrixFromFile(patha)

        pathtok = patha.split("-")
        row = pathtok[2][1:]
        filename = pathtok[0]+"-c-r"+str(row)+'-p'+str(rank).zfill(2)+'.json'
        out.setRow(row)
        out.setResult(filename)
        out.setRank(rank)

        t0 = ut.current_milli_time()
        c = prod(a,b)
        
        out.setTime(ut.current_milli_time() - t0)
        ut.writeMatrixToFile(c, filename)

        comm.send(out.toJSON(), dest=0)
    comm.send("stop", dest=0)

MPI.Finalize()


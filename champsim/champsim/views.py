from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from os import walk, system
from collections import namedtuple
import os, threading, math, time
from datetime import datetime
from . import hybridizeit
class bps:
    name = str
    time = str
    traces = int
    builded = bool
    avg_accuracy = float
    traceslist = list
class trace_:
    name = str
    num = str
    size = str
    bestpred = str
    accuracybest = float
Pair = namedtuple("Pair", ["first", "second"])

def home(request):
    return render(request,"index.html")

def build(request):
    f = []
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/branch/"):
        f = filenames
        break
    binx = []
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/bin/"):
        binx = filenames
        break
    # print(binx,f)
    branch_preds = []    
    for i in f:
        if(i.find(".bpred")!=-1):
            branch_preds.append(i[:i.find(".bpred")])
    hash_preds = {}
    goto_page = []
    for i in branch_preds:
        new = bps()
        new.traceslist = []
        new.name = i
        new.avg_accuracy=0
        try:
            new.time = datetime.fromtimestamp(os.path.getmtime("/mnt/c/Studies/projects/COA/champsim-master/bin/"+i+"-no-no-no-no-lru-1core"))
            new.builded = 1
        except:
            new.builded = 0
        new.traces = 0
        hash_preds[i] = new
    outputs = []
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/results_10M"):
        outputs = filenames
        break
    for i in outputs:
        file = open("/mnt/c/Studies/projects/COA/champsim-master/results_10M/"+i,'r')
        tracename = i[:i.find(".champsimtrace.xz")]
        x = "".join(file.readlines())
        index = x.find("Prediction Accuracy: ")
        if(index!=-1):
            ind = i.find(".xz-")
            ind+=4
            bpname = i[ind:]
            bpname = bpname[:bpname.find("-")]
            ind2=x[index+21:].find("%")
            x = x[index+21:]
            x = x[:ind2]
            hash_preds[bpname].traces+=1
            x = float(x)
            hash_preds[bpname].avg_accuracy=hash_preds[bpname].avg_accuracy+x
            hash_preds[bpname].traceslist.append(Pair(tracename,str(x)+"%"))
    for i in list(hash_preds.keys()):
        if(hash_preds[i].traces!=0):
            hash_preds[i].avg_accuracy = float(str(hash_preds[i].avg_accuracy/hash_preds[i].traces)[:str(hash_preds[i].avg_accuracy/hash_preds[i].traces).find(".")+5])
        else:
            hash_preds[i].avg_accuracy = 0
    for i in list(hash_preds.keys()):
        goto_page.append(hash_preds[i])
    builted = [0,1]
    context = {"branch_preds":goto_page,"build":1,"unbuild":2}
    return render(request,"build.html",context)


def run(request):
    f = []
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/dpc3_traces/"):
        f = filenames
        break
    alltraces = []
    for i in f:
        i=i[:i.find(".champsim")]
        if(i!="desktop.in"):
            size = os.stat("/mnt/c/Studies/projects/COA/champsim-master/dpc3_traces/"+i+".champsimtrace.xz").st_size
            new = trace_()
            new.name = i
            new.size = size/1000000
            new.num = i[:3]
            new.accuracybest = 0
            alltraces.append(new)
    binx = []
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/bin/"):
        binx = filenames
        break
    # print(binx,f)
    branch_preds = []    

    for i in binx:
        branch_preds.append(i[:i.find("-no")])
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/results_10M"):
        outputs = filenames
        break
    for j in alltraces:
        for i in outputs:
            file = open("/mnt/c/Studies/projects/COA/champsim-master/results_10M/"+i,'r')
            pp = i.find(".champsimtrace.xz")
            tracename = i[:pp]
            if(j.name==tracename):
                # print(predname)
                x = "".join(file.readlines())
                index = x.find("Prediction Accuracy: ")
                if(index!=-1):
                    ind = i.find(".xz-")
                    ind+=4
                    bpname = i[ind:]
                    bpname = bpname[:bpname.find("-")]
                    ind2=x[index+21:].find("%")
                    x = x[index+21:]
                    x = x[:ind2]
                    if(float(x)>j.accuracybest):
                        j.bestpred = bpname
                        j.accuracybest = float(x)
    context = {"traces":alltraces,"BP":branch_preds}
    return render(request,"run.html",context)


def building(bpred):
    print("yes")
    os.system("cd /mnt/c/Studies/projects/COA/champsim-master/ ; ./build_champsim.sh {} no no no no lru 1".format(bpred))
@csrf_exempt
def jsonbuild(request):
    print(request)
    bpred = request.body.decode()
    if(os.path.isfile('/mnt/c/Studies/projects/COA/champsim-master/bin/{}-no-no-no-no-lru-1core'.format(bpred))==1):
        os.remove('/mnt/c/Studies/projects/COA/champsim-master/bin/{}-no-no-no-no-lru-1core'.format(bpred))
    print(bpred)
    t = time.time()
    building(bpred)
    t = time.time()-t
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/bin/"):
        binx = filenames
        break
    if(bpred+"-no-no-no-no-lru-1core" not in binx):
        built = 0
    else:
        built = 1
    return JsonResponse({"Build Started":built,"time":t})
    
def edit(request):
    return render(request,"BP_editor_champsim.html")

@csrf_exempt
def running(request):
    all = request.body.decode()
    ind = all.find("^^&&")
    trace = all[:ind]
    bp = all[ind+4:]
    here = time.time()
    os.system("cd /mnt/c/Studies/projects/COA/champsim-master/ ; ./run_champsim.sh {}-no-no-no-no-lru-1core 1 10 {}".format(bp,trace+".champsimtrace.xz"))
    here = time.time()-here
    file = open("/mnt/c/Studies/projects/COA/champsim-master/results_10M/{}{}.txt".format(trace+".champsimtrace.xz-",bp+"-no-no-no-no-lru-1core"),"r")
    this = "".join(file.readlines())
    index = this.find("Prediction Accuracy: ")
    ind2=this[index+21:].find("%")
    this = this[index+21:]
    this = this[:ind2]
    print(this)
    return JsonResponse({"time":str(here)[:6],"accu":this+"%"})

def hybridize(request):
    for (dirpath, dirnames, filenames) in walk("/mnt/c/Studies/projects/COA/champsim-master/bin/"):
        binx = filenames
        break
    # print(binx,f)
    branch_preds = []    
    for i in binx:
        branch_preds.append(i[:i.find("-no")])
    return render(request,"hybridize.html",{"bp":branch_preds})

@csrf_exempt
def hybridmake(request):
    preds = request.body.decode()
    pred1 = preds[:preds.find("^^&&")]
    pred2 = preds[preds.find("^^&&")+4:]
    ans = hybridizeit.hybridizing_two(pred1,pred2)
    return JsonResponse({"done":ans})
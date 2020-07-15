from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from os import walk, system
from collections import namedtuple
import os, threading, math, time
from datetime import datetime
from pathlib import Path
from . import hybridizeit
import multiprocessing
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
path_of_champsim = str(Path(__file__).parents[2])

def home(request):
    print(path_of_champsim)
    return render(request,"index.html")

def build(request):
    f = []
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/branch/"):
        f = filenames
        break
    binx = []
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/bin/"):
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
            new.time = datetime.fromtimestamp(os.path.getmtime(path_of_champsim+"/champsim-master/bin/"+i+"-no-no-no-no-lru-1core"))
            new.builded = 1
        except:
            new.builded = 0
        new.traces = 0
        hash_preds[i] = new
    outputs = []
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/results_10M"):
        outputs = filenames
        break
    for i in outputs:
        file = open(path_of_champsim+"/champsim-master/results_10M/"+i,'r')
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
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/dpc3_traces/"):
        f = filenames
        break
    alltraces = []
    for i in f:
        i=i[:i.find(".champsim")]
        if(i!="desktop.in"):
            size = os.stat(path_of_champsim+"/champsim-master/dpc3_traces/"+i+".champsimtrace.xz").st_size
            new = trace_()
            new.name = i
            new.size = size/1000000
            new.num = i[:3]
            new.accuracybest = 0
            alltraces.append(new)
    binx = []
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/bin/"):
        binx = filenames
        break
    # print(binx,f)
    branch_preds = []    

    for i in binx:
        branch_preds.append(i[:i.find("-no")])
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/results_10M"):
        outputs = filenames
        break
    for j in alltraces:
        for i in outputs:
            file = open(path_of_champsim+"/champsim-master/results_10M/"+i,'r')
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
    os.system("cd "+path_of_champsim+"/champsim-master/ ; ./build_champsim.sh {} no no no no lru 1".format(bpred))
@csrf_exempt
def jsonbuild(request):
    print(request)
    bpred = request.body.decode()
    if(os.path.isfile(path_of_champsim+'/champsim-master/bin/{}-no-no-no-no-lru-1core'.format(bpred))==1):
        os.remove(path_of_champsim+'/champsim-master/bin/{}-no-no-no-no-lru-1core'.format(bpred))
    print(bpred)
    t = time.time()
    building(bpred)
    t = time.time()-t
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/bin/"):
        binx = filenames
        break
    if(bpred+"-no-no-no-no-lru-1core" not in binx):
        built = 0
    else:
        built = 1
    return JsonResponse({"Build Started":built,"time":t})
    
def edit(request):
    return render(request,"BP_editor_champsim.html")


def runthis(ret_value,bp,trace):
    os.system("cd "+path_of_champsim+"/champsim-master/ ; ./run_champsim.sh {}-no-no-no-no-lru-1core 1 10 {}".format(bp,trace+".champsimtrace.xz"))
    ret_value.Value = 1

@csrf_exempt
def running(request):
    all = request.body.decode()
    ind = all.find("^^&&")
    trace = all[:ind]
    bp = all[ind+4:]
    ret_value = multiprocessing.Value("d", 0.0, lock=False)
    reader_process = multiprocessing.Process(target=runthis, args=[ret_value,bp,trace])
    here = time.time()
    reader_process.start()
    reader_process.join()
    here = time.time()-here
    file = open(path_of_champsim+"/champsim-master/results_10M/{}{}.txt".format(trace+".champsimtrace.xz-",bp+"-no-no-no-no-lru-1core"),"r")
    this = "".join(file.readlines())
    index = this.find("Prediction Accuracy: ")
    ind2=this[index+21:].find("%")
    this = this[index+21:]
    this = this[:ind2]
    print(ret_value.value)
    return JsonResponse({"time":str(here)[:6],"accu":this+"%"})

def hybridize(request):
    for (dirpath, dirnames, filenames) in walk(path_of_champsim+"/champsim-master/bin/"):
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
    time.sleep(1)
    ans = hybridizeit.hybridizing_two(pred1,pred2)
    return JsonResponse({"done":ans})


code_of_the_predictor = ""

@csrf_exempt
def code(request):
    global code_of_the_predictor
    code_of_the_predictor = request.body.decode()
    return JsonResponse({"code":"BP_editor_read_write"})

def codeit(request):
    file = open(path_of_champsim+"/champsim-master/branch/"+code_of_the_predictor[:-4]+".bpred","r")
    givecode = "".join(file.readlines())
    return render(request,"code.html",{"code":givecode,"predictor":code_of_the_predictor[:-4]})

@csrf_exempt
def saveit(request):
    code = request.body.decode()
    file = open(path_of_champsim+"/champsim-master/branch/"+code_of_the_predictor[:-4]+".bpred","w")
    file.write(code)
    file.close()
    time.sleep(0.5)
    return JsonResponse({"done":1})

@csrf_exempt
def addit(request):
    global code_of_the_predictor
    code = request.body.decode()
    code_of_the_predictor = code[:code.find("^^&&")]+"4444"
    code = code[code.find("^^&&")+4:]
    file = open(path_of_champsim+"/champsim-master/branch/"+code_of_the_predictor[:-4]+".bpred","w")
    file.write(code)
    file.close()
    return JsonResponse({"1":1})
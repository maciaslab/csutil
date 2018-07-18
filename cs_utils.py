import urllib
import os
import zipfile
import progressbar
import requests
import json
from termcolor import colored
from tabulate import tabulate
import gzip
import shutil
import random
from string import letters
import natsort
import sys

#Requires: bedtools
#Citations
#Quinlan AR and Hall IM, 2010. BEDTools: a flexible suite of utilities for comparing genomic features. Bioinformatics 26(6):841-842.
 
"""cs_utils module

Various utility functions shared amongst cs_utils programs

"""
pbar = None
defaults={
    'dataPath': './data/',
    'version':'v0.1',
    'progStringColor':'yellow'

    }

if (os.environ.get('GENOME_DATAPATH') != None):
        defaults['dataPath']= os.environ['GENOME_DATAPATH']

def IUPACtoREGEXP(seq):
    #Stubbed
    to_regex = { "A":"A", "B":"[CGT]", "C":"C", "D":"[AGT]", "G":"G", "H":"[ACT]", "K":"[GT]", "M":"[AC]", "N":"[ACGT]", "R":"[AG]", "S":"[GC]", "T":"T", "V":"[ACG]", "W":"[AT]", "Y":"[CT]" }
    ret_seq=""
    for nuc in seq:
        #print nuc+" "+revseq
        ret_seq=ret_seq+to_regex[nuc.upper()]
    return ret_seq

def rev_comp(seq):

    compls = { "A":"T", "B":"V", "C":"G", "D":"H", "G":"C", "H":"D", "K":"M", "M":"K", "N":"N", "R":"Y", "S":"S", "T":"A", "V":"B", "W":"W", "Y":"R" }
    revseq=""
    for nuc in seq:
        #print nuc+" "+revseq
        revseq=compls[nuc.upper()]+revseq
    return revseq

def concatenateFiles(infile_names,outfile_name):
    with open(outfile_name, 'w') as outfile:
        for fname in infile_names:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)

def printProgString():
    
        print(colored("\n"+os.path.basename(sys.argv[0])+" "+getDefault('version')+" Pau Martin Malpartida pau.martin@irbbarcelona.org\n",getDefault('progStringColor')))
    

def cleanBed(inputbed, outputbed,uniq=False):
    bedFileHandle=open(outputbed,"w")
    inFileHandle=open(inputbed)
    data=inFileHandle.readlines()
    header=""
    if (data[0].split()[0].upper() =="TRACK"):
        header=data.pop(0)
    natsort_key = natsort.natsort_keygen()
    #data.sort(key=lambda l: cs_utils.joinChr_start(l))
    data.sort(key=natsort_key)

    if uniq:
        existing=set()
        newdata=[]
        for item in data:
            sp=item.split('\t')
            sign=str(sp[0])+"."+str(sp[1])+"."+str(sp[2])
            if sign not in existing:
                newdata.append(item)
                existing.add(sign)
        data=newdata 
    if (header !=""):
        data.insert(0,header)
    bedFileHandle.writelines(data)

def removeletters(mystring):
    return mystring.translate(None, letters)

def joinChr_start(line):
    a=line.split('\t')
    if (len(a)<3):
        return 0
    chrnum=removeletters(a[0])
    returnvalue=float(str(chrnum)+"."+str(a[1]))
    #print line+" "+str(returnvalue)
    return returnvalue


def getDefault(key):
    global defaults
    if key in defaults:
        return defaults[key]
    else:
        return None

def showProgress(done, total_size):
    global pbar
    if pbar is None:

        widgets = ["Size:", humanBytes(total_size), "", progressbar.FileTransferSpeed(
        ), " ", progressbar.Bar(), ' ', progressbar.Percentage(), ' ', progressbar.ETA()]
        pbar = progressbar.ProgressBar(
            widgets=widgets, maxval=total_size).start()

    if done < total_size:
        pbar.update(done)
    else:
        pbar.update(total_size)


def showProgressDownload(block_num, block_size, total_size):
    global pbar
    if pbar is None:

        widgets = ["Size:", humanBytes(total_size), "", progressbar.FileTransferSpeed(
        ), " ", progressbar.Bar(), ' ', progressbar.Percentage(), ' ', progressbar.ETA()]
        pbar = progressbar.ProgressBar(
            widgets=widgets, maxval=total_size).start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


def finishProgress():
    global pbar
    pbar.finish()
    pbar = None


def downloadFile(url, filename):
    print "Downloading "+url+" to "+filename
    urllib.urlretrieve(url, filename, showProgressDownload)


def humanBytes(B):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string"""
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B/GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B/TB)


def randomColor(max=255):
    """Get an hex random color.

    Keyword arguments:
    max -- max intensity for each hex component (default 255)
    """
    a = random.randint(0, 255)
    b = random.randint(0, 255)
    c = random.randint(0, 255)

    while (a+b+c > (max*3)):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
    return str(a)+","+str(b)+","+str(c)

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def getbedtools(verbose=True,quit_err=True):
    bedtools_exec=which("bedtools")
    if (bedtools_exec):
        if (verbose):
            print "bedtools executable found: "+ bedtools_exec
    else:
        if (verbose):
            print "bedtools executable not found. Install bedtools from http://bedtools.readthedocs.io/en/latest/"
        if (quit_err):
            exit(1)
    return bedtools_exec

def getfuzznuc(verbose=True,quit_err=True):
    fuzznuc_exec=which("fuzznuc")
    if (fuzznuc_exec):
        if (verbose):
            print "fuzznuc executable found: "+ fuzznuc_exec
    else:
        if (verbose):
            print "fuzznuc executable not found. Install emboss from http://emboss.sourceforge.net/"
        if (quit_err):
            exit(1)
    return fuzznuc_exec
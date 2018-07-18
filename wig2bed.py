#!/usr/bin/python
# coding: utf-8
import argparse
import os
import zipfile
import progressbar
import json
from termcolor import colored
from tabulate import tabulate
import tempfile
import time
import random
import shutil
import sys
import cs_utils


startTime = time.time()

parser = argparse.ArgumentParser(description='Convert fixedStep wig file to bed')
parser.add_argument('input', type=str, help='input wig file')
parser.add_argument('--outfile', help='output file name . Default is inputfile+".bed"')
parser.add_argument('--outfile_int', help='output (internal bed) file name . Default is inputfile+"INT.bed"')

cs_utils.printProgString()
args = parser.parse_args()

print "Input: "+args.input


tempdir=tempfile.mkdtemp()
outfile=args.input+".bed"
outfile_int=args.input+".INT.bed"
if args.outfile:
	outfile=args.outfile
if args.outfile_int:
	outfile_int=args.outfile_int
print "Output: "+outfile
print "Internal Output: "+outfile_int
ofh= open (tempdir+"/tmp.bed","w")
ofih= open (tempdir+"/tmp2.bed","w")
j=0
track=-1
cr=""
start=""
end=""
step=0
with open(args.input,"r") as g:
		for line in g:
			j+=1
			if line[0:5]=="track":
				track+=1
				continue
			if track:
				ofih.write(line)
			else:
				spline=line.split(" ")
				if spline[0]=="fixedStep":
					if (cr!=""):
						ofh.write("%s\t%s\t%s\n" % (cr,str(start),str(end)))
					cr=spline[1].split("=")[1]
					start=int(spline[2].split("=")[1])-1
					end=int(start)
					step=spline[3].split("=")[1]
				else:
					end+=int(step)

ofh.write("%s\t%s\t%s\n" % (cr,str(start),str(end)))
ofh.close()
ofih.close()

print "Sorting..."

cs_utils.cleanBed(tempdir+"/tmp.bed",outfile,True)
cs_utils.cleanBed(tempdir+"/tmp2.bed",outfile_int,True)
shutil.rmtree(tempdir)


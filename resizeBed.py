#!/usr/bin/python
# coding: utf-8
import argparse
import urllib
import os
import zipfile
import progressbar
import requests
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

parser = argparse.ArgumentParser(description='Resize peaks in a bed file to new widths, centered in original position.')
parser.add_argument('inputBed', type=str, help='input bed file')
parser.add_argument('--outfile', help='output file name . Default is input name + "_resized_"+size+".bed"')
parser.add_argument('--size', help='size of the promoter in bp (default:200)')

cs_utils.printProgString()
args = parser.parse_args()

print "Input: "+args.inputBed


size=200
if args.size:
	size=args.size


tempdir=tempfile.mkdtemp()
outputBed=args.inputBed[:-4]+"_resized_"+str(size)+".bed"
if args.outfile:
	outputBed=args.outfile
#Check if files exist, exit if not.
if not os.path.isfile(args.inputBed):
	print "File "+args.inputBed+" not found."
	exit(1)

print "Input: "+args.inputBed
print "Output: "+outputBed
print "Size: "+str(size)

outfileHandle=open(tempdir+"/tmp.bed","w")
with open(args.inputBed,"r") as g:
		for line in g:
			if line[0:5] != "track":
				spline=line.split()
				half=(int(spline[1])+int(spline[2]))/2
				start=half-(size/2)
				end=half+(size/2)
				outfileHandle.write("%s\t%s\t%s" % (spline[0],str(start),str(end)))
				if len(spline)>3:
					outfileHandle.write("\t%s\t%s" % (spline[3],spline[4]))
				if len(spline)>5:
					outfileHandle.write("\t%s" % (spline[5]))
				if len(spline)>6:
					outfileHandle.write("\t%s\t%s" % (start,end))
				if len(spline)>8:
					outfileHandle.write("\t%s" % spline[8])
				outfileHandle.write("\n")

outfileHandle.close()


print "Sorting..."
cs_utils.cleanBed(tempdir+"/tmp.bed",outputBed,True)
shutil.rmtree(tempdir)



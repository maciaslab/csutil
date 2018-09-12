#!python
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

import shutil
import sys
import cs_utils 



startTime = time.time()

parser = argparse.ArgumentParser(description='Generate a bed file Covering the promoter regions.')
parser.add_argument('assembly', type=str, help='assembly to use (ex: mm10, hg19)')
parser.add_argument('--outfile', help='output file name . Default is assembly name + "_promoter_"+size+".bed"')
parser.add_argument('--color', help='color, as a RGB triplet, comma separated (ex:"250,120,120")')
parser.add_argument('--size', help='size of the promoter in bp, upstream the TSS (default:1000)')
parser.add_argument('--sizeDown', help='size of the promoter in bp, downstream the TSS (default:0)')
parser.add_argument('--dataPath', help='set the dataPath')

cs_utils.printProgString()
args = parser.parse_args()



tempdir=tempfile.mkdtemp()



promSize=1000
promSizeDown=0
if args.size:
	promSize=int(args.size)

if args.sizeDown:
	promSizeDown=int(args.sizeDown)

dataPath = cs_utils.getDefault('dataPath')+"/genomes/"
if args.dataPath:
	dataPath=args.dataPath+"/genomes/"


color=cs_utils.randomColor(200)
if args.color:
	color=args.color


bedFile=args.assembly+"_promoter_-"+str(promSize)+"_+_"+str(promSizeDown)+".bed"
if args.outfile:
	bedFile=args.outfile



geneFile=dataPath+"/genomes/"+args.assembly+"/"+"refGene.txt"
if not os.path.isfile(geneFile):
	print ("File "+geneFile+" not found. Download genome with:")
	print ("downloadgenome.py "+args.assembly)
	exit(1)


geneFile=geneFile.rstrip()

print ("Writing promoter bed for genome "+args.assembly+" to " + bedFile)
print ("Generating bed file from -%i to +%i from TSS" %(promSize,promSizeDown))
bedFileHandle=open(tempdir+"/tmp.bed","w")
with open(geneFile,"r") as f:
		for line in f:
			spline=line.split()
			strand=spline[3]
			start=0
			end=0
			if strand =="+":
				end=int(spline[4])
				start=end-(promSize+1)
				end=end+promSizeDown
			else:
				start=int(spline[5])
				end=start+(promSize+1)
				start=start-promSizeDown
			if start<0:
				start=0
			if end<0:
				end=0
			bedFileHandle.write("%s\t%s\t%s\t%s\t0\t%s\t%s\t%s\t%s\n" %(spline[2],start,end,spline[12],spline[3],start,end,color))
bedFileHandle.close()


print ("Sorting...")
cs_utils.cleanBed(tempdir+"/tmp.bed",bedFile,True)
shutil.rmtree(tempdir)



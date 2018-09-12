#!python
# coding: utf-8
import argparse
import os
import progressbar
import tempfile
import shutil
import cs_utils

pbar= None


parser = argparse.ArgumentParser(description='Merge and sort any number of bed files into one.')
parser.add_argument('bed', type=str, nargs="+", help='bed file to merge')
parser.add_argument('--outfile', help='output file name . Default is "merged.bed"')
parser.add_argument('--uniq', action="store_true",help='Remove duplicate entries.' )

cs_utils.printProgString()
args = parser.parse_args()





refreshEvery=10000
bytesSize=0
doneSize=0
outFile="merged.bed"
tempdir=tempfile.mkdtemp()

if args.outfile:
	outFile=args.outfile

for item in args.bed:
	if os.path.isfile(item):
		#print item
		itemInfo = os.stat(item)
		bytesSize+=itemInfo.st_size
	else:
		print ("File "+item+" not found.")
		exit(1)

print ("Writing to "+outFile)

outBed=open(tempdir+"/tmp.bed","w")


print ("Merging...")

loop=0
for item in args.bed:
	with open(item,"r") as f:
		for line in f:
			doneSize+=(len(line)+1)
			loop+=1
			if line[0:5] != "track":
				outBed.write(line)
				if (loop % refreshEvery):
					cs_utils.showProgress(doneSize, bytesSize)

outBed.close()
cs_utils.finishProgress()


print ("Sorting...")
cs_utils.cleanBed(tempdir+"/tmp.bed",outFile,args.uniq)
shutil.rmtree(tempdir)

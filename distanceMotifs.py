#!/usr/bin/python
# coding: utf-8
import argparse
import os
import progressbar
import tempfile
import shutil
import collections
import cs_utils
import math
import pandas as pd

#Experimental


parser = argparse.ArgumentParser(description='Shows intermotif distances (from a motif bed file) in regions delimited from another bed file.')
parser.add_argument('motifs', type=str, help='Bed file containing motifs')
parser.add_argument('regions', help='Bed file with the regions to count motifs in')
parser.add_argument('--outfile', help='output file name . Default is region bed filename + "_dist.csv"')
parser.add_argument('--tsv', action="store_true",help='Output is .tsv instead of .csv')
parser.add_argument('--plot', action="store_true",help='Plot histogram in terminal')

cs_utils.printProgString()
args = parser.parse_args()

distances=[]
bedtools_exec=cs_utils.getbedtools()
motifsBed=args.motifs
regionsBed=args.regions
SEP=","
extension=".csv"
if args.tsv:
	SEP="\t"
	extension=".tsv"
outFile=regionsBed+"_dist"+extension

if args.outfile:
	outFile=args.outfile

#Check if files exist, exit if not.
if not os.path.isfile(motifsBed):
	print ("File "+motifsBed+" not found.")
	exit(1)
if not os.path.isfile(regionsBed):
	print ("File "+regionsBed+" not found.")
	exit(1)

tempdir=tempfile.mkdtemp()

#Get motifs only in regions file. This makes the file smaller.
miniBedTemp=tempdir+"/tempmotifs.bed"
miniBed=tempdir+"/tempmotifs2.bed"
command=bedtools_exec +" intersect -a "+motifsBed+" -b "+ regionsBed+" >"+miniBedTemp
os.system(command)
#Sort and remove duplicates
cs_utils.cleanBed(miniBedTemp,miniBed,True)
motifDict=collections.OrderedDict()

#Open new bedfile and list motifs.
with open(miniBed,"r") as f:
	for line in f:
		spline=line.split()
		myMotif=spline[3]
		if myMotif in motifDict:
			motifDict[myMotif]+=1
		else:
			motifDict[myMotif]=1

emptyCountDict=collections.OrderedDict()
print ("Motifs found (total):")
for key,value in motifDict.items():
	print ("%s: %i" % (key,value))
	emptyCountDict[key]=0



print ("Writing to "+outFile)




#Count motifs.
totalLines=0
with open(regionsBed,"r") as f:
	for line in f:
		totalLines+=1

myLine=0
with open(regionsBed,"r") as f:

	for line in f:
		countDict=collections.OrderedDict(emptyCountDict)
		myLine+=1
		#cs_utils.showProgress(myLine,totalLines)
		
		if line[0:5] != "track":
			spline=line.split()
			cr=spline[0]
			start=int(spline[1])
			end=int(spline[2])
			regionField=cr+":"+str(start)+"-"+str(end)
			#print (regionField)
			positions=[]
			#print("--------")
			with open(miniBed,"r") as g:
					for lineg in g:
							if lineg[0:5] != "track":
								splineg=lineg.split()
								crg=splineg[0]
								startg=int(splineg[1])
								endg=int(splineg[2])
								motifg=splineg[3]
								middle=int(math.floor((startg+endg)/2))
								if (cr==crg) and ((startg>=start and startg<=end) or (endg>=start and endg<=end)):
									#print (lineg)
									#print (motifg,middle)
									positions.append(middle)
									countDict[motifg]+=1
			#print("***")
			#print(positions)
			while (len(positions) != 0):

					p=positions.pop()
					for value in positions:
						mydiff=abs(p-value)
						distances.append(mydiff)
						#print("*," +str(mydiff))
				


#print(distances)
df=pd.DataFrame(distances)
counts=df.stack().value_counts()
counts=pd.DataFrame({'distance':counts.index,'frequency':counts.values})
counts=counts.sort_values(by=['distance'])
counts=counts[['distance','frequency']]
#print (counts)
counts.to_csv(outFile,index=False,sep=SEP)
#print(miniBed)
if args.plot:
	from bashplotlib.histogram import plot_hist 
	plot_hist(distances,bincount=80,xlab=True,pch="█")
shutil.rmtree(tempdir)

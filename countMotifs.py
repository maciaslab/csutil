#!/usr/bin/python
# coding: utf-8
import argparse
import os
import progressbar
import tempfile
import shutil
import collections
import cs_utils

# Requires: bed file of motifs (made with bedmotif + mergebed)
# bed file of Chipseq (regions)
#Produces: CSV file with count of motif per each region and counts per Kb per region


parser = argparse.ArgumentParser(description='Count motifs (in a bed file) in regions delimited from another bed file.')
parser.add_argument('motifs', type=str, help='Bed file containing motifs')
parser.add_argument('regions', help='Bed file with the regions to count motifs in')
#parser.add_argument('--name', help='motif name. Default is "MOTIFS"' )
parser.add_argument('--outfile', help='output file name . Default is region bed filename + ".csv"')
parser.add_argument('--tsv', action="store_true",help='Output is .tsv instead of .csv')

cs_utils.printProgString()
args = parser.parse_args()

bedtools_exec=cs_utils.getbedtools()
motifsBed=args.motifs
regionsBed=args.regions
SEP=","
extension=".csv"
if args.tsv:
	SEP="\t"
	extension=".tsv"
outFile=regionsBed+extension

if args.outfile:
	outFile=args.outfile

#Check if files exist, exit if not.
if not os.path.isfile(motifsBed):
	print "File "+motifsBed+" not found."
	exit(1)
if not os.path.isfile(regionsBed):
	print "File "+regionsBed+" not found."
	exit(1)

tempdir=tempfile.mkdtemp()

#Get motifs only in regions file. This makes the file smaller.
miniBed=tempdir+"/tempmotifs.bed"
command=bedtools_exec +" intersect -a "+motifsBed+" -b "+ regionsBed+" >"+miniBed
os.system(command)

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
print "Motifs found (total):"
for key,value in motifDict.iteritems():
	print "%s: %i" % (key,value)
	emptyCountDict[key]=0



print "Writing to "+outFile
output=open(outFile,"w")
output.write("REGION")
for key,value in motifDict.iteritems():
	output.write(SEP+key)
output.write(SEP+"SIZE")
for key,value in motifDict.iteritems():
	output.write(SEP+key+"/Kb")

output.write("\n")


#Count motifs.
totalLines=0
with open(regionsBed,"r") as f:
	for line in f:
		totalLines+=1

myLine=0
totalSize=0
with open(regionsBed,"r") as f:

	for line in f:
		countDict=collections.OrderedDict(emptyCountDict)
		myLine+=1
		cs_utils.showProgress(myLine,totalLines)
		
		if line[0:5] != "track":
			spline=line.split()
			cr=spline[0]
			start=int(spline[1])
			end=int(spline[2])
			regionField=cr+":"+str(start)+"-"+str(end)
			with open(miniBed,"r") as g:
					for lineg in g:
							if lineg[0:5] != "track":
								splineg=lineg.split()
								crg=splineg[0]
								startg=int(splineg[1])
								endg=int(splineg[2])
								motifg=splineg[3]

								
								if (cr==crg) and ((startg>=start and startg<=end) or (endg>=start and endg<=end)):
									countDict[motifg]+=1

			
			output.write(regionField)
			for key,value in countDict.iteritems():
				output.write(SEP+str(value))
			size=int(end)-int(start)
			totalSize+=size
			output.write(SEP+str(size))
			for key,value in countDict.iteritems():
				output.write(SEP+str((float(value)/float(size))))
			output.write("\n")

output.close()
#Write statistics.
print "Motifs found (per Kb):"
for key,value in motifDict.iteritems():
	print "%s: %.2f motifs/Kb" % (key,(float(value)/totalSize)*1000)

print "Motifs found (per region):"
for key,value in motifDict.iteritems():
	print "%s: %.2f motifs/region" % (key,(float(value)/myLine))
print "Average region size: %i bp" %( totalSize/myLine)
print "Number of regions: %i" % (myLine)
shutil.rmtree(tempdir)

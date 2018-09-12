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
import random
import shutil
import sys
import cs_utils
from Bio import SeqIO
import regex as re


startTime = time.time()

IUPAChelp="""
This is the list of the IUPAC nucleotide codes, used in motif search

K=[GT]
M=[AC]
W=[AT]
Y=[CT]
R=[AG]
S=[GC]

V=[ACG]
B=[CGT]
D=[AGT]
H=[ACT]

N=[ACGT]
"""

parser = argparse.ArgumentParser(description='Generate a bed file containing the defined motifs from a fasta file (Usually a genome).',formatter_class=argparse.RawDescriptionHelpFormatter,epilog=IUPAChelp)
parser.add_argument('fasta', type=str, help='fasta file to use or assembly (ex: mygenome.fasta, mm10, hg19)')
parser.add_argument('motifs', help='list of motifs (comma separated)')
parser.add_argument('--name', help='motif name. Default is "MOTIFS"' )
parser.add_argument('--outfile', help='output file name . Default is motif name + ".bed"')
parser.add_argument('--color', help='color, as a RGB triplet, comma separated (ex:"250,120,120")')
parser.add_argument('--dataPath', help='set the dataPath')
parser.add_argument('--all_chromosomes', action="store_true", help='by default, it ignores unlocalized/unplaced/alternate sequences in genomes. Enabling this flag disables this functionality')

cs_utils.printProgString()
args = parser.parse_args()



#fuzznuc_exec=cs_utils.getfuzznuc()

dataPath = cs_utils.getDefault('dataPath')+"/genomes/"
if args.dataPath:
	dataPath=args.dataPath+"/genomes/"


trackName="MOTIFS"
if args.name:
	trackName=args.name

#color="33,64,154"
color=cs_utils.randomColor(200)
if args.color:
	color=args.color

bedFile=trackName+".bed"
if args.outfile:
	bedFile=args.outfile
motifname=trackName

if os.path.isfile(args.fasta):
	fastaFile = args.fasta
elif os.path.isfile(dataPath+"/genomes/"+args.fasta+"/"+args.fasta+".fasta"):
	fastaFile = dataPath+"/genomes/"+args.fasta+"/"+args.fasta+".fasta"
elif os.path.isfile(dataPath+"/genomes/"+args.fasta+"/"+args.fasta+".fa"):
	fastaFile = dataPath+"/genomes/"+args.fasta+"/"+args.fasta+".fa"	
else:
	print ("Fasta file not found. If it is a genome, dowload it with:\ndownloadgenome "+args.fasta)
	exit(1)


print ("Generating: "+bedFile)
tempdir=tempfile.mkdtemp()





motiflist=[]
reversemotiflist=[]
for i in args.motifs.split(","):
	motiflist.append(cs_utils.IUPACtoREGEXP(i))
	reversemotiflist.append(cs_utils.IUPACtoREGEXP(cs_utils.rev_comp(i)))


motif="|".join(motiflist)
print ("Searching for the following motifs:")
print ("Chain+:")
for i in motiflist:
	print(i)
print ("Chain-:")
for i in reversemotiflist:
	print(i)	


skip_underscores=not(args.all_chromosomes)
if (skip_underscores):
	print("Skipping unlocalized/unplaced/alternate sequences")

records = list(SeqIO.parse(fastaFile, "fasta"))
chain="+"
reparser=re.compile(motif)

bedFileHandle=open(tempdir+"/tmp.bed","w")
bedFileHandle.write('track name='+trackName+' description="NEW" itemRgb="On"'+"\n")



for item in records:
	
	if (skip_underscores):
		if "_" in str(item.id):
			continue

	iterator= reparser.finditer(
		(str(item.seq)).upper(),overlapped=True
		)
	for match in iterator:
		bedFileHandle.write("%s\t%i\t%i\t%s\t0\t%s\t%i\t%i\t%s\n" % (item.id,match.start(),match.end(),motifname,chain,match.start(),match.end(),color ) )



chain="-"
motif="|".join(reversemotiflist)
reparser=re.compile(motif)
for item in records:
	#print (item.id)
	iterator= reparser.finditer((str(item.seq)).upper(),overlapped=True)
	for match in iterator:
		bedFileHandle.write("%s\t%i\t%i\t%s\t0\t%s\t%i\t%i\t%s\n" % (item.id,match.start(),match.end(),motifname,chain,match.start(),match.end(),color ) )

bedFileHandle.close()
print ("Sorting...")
#print (tempdir+"/tmp.bed")
cs_utils.cleanBed(tempdir+"/tmp.bed",bedFile,False)
shutil.rmtree(tempdir)



endTime = time.time()
print ("Execution time: %i seconds" % (endTime-startTime))

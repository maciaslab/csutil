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
import pandas
import cs_utils

startTime = time.time()

parser = argparse.ArgumentParser(
    description='Reads a csv file from countMotifs and prints statistics')
parser.add_argument('inputCSV', type=str, help='input CSV file')
parser.add_argument(
    '--outfile', help='output file name . Default is "motifcount.csv"')
parser.add_argument(
    '--combine', help='Combine (add) many motifs into one group. Sepparated by commas, first is group name. Ex:"5GC,GGCCG,GGCGC,GGCTG,GGCGG"')

cs_utils.printProgString()
args = parser.parse_args()

print ("Input: "+args.inputCSV)

SEP = ","
inputFile = args.inputCSV
outFile = "motifcount.csv"
if args.outfile:
    outFile = args.outfile
print ("Output: "+outFile+"\n")

if not (os.path.isfile(inputFile)):
    print ("\nERROR: %s not found\n" % (inputFile))
    exit(1)
df = pandas.read_csv(inputFile)
colname = ""
if args.combine:
    splc = args.combine.split(",")
    colname = splc.pop(0)
    df[colname] = 0
    for nam in splc:
        if not (nam in df.columns):
            print ("ERROR: %s is not a valid motif in the datafile. The file %s contains the following motifs:" %(nam,inputFile))
            size_col = df.columns.get_loc("SIZE")

            for i in range(1, size_col):
                print (df.columns[i])
            exit(1)
        df[colname] = df[nam]+df[colname]

#print df
size_col = df.columns.get_loc("SIZE")
bins = [-1, 0, 1, 2, 1000]
group_names = ["0", "1", "2", "3+"]
#print "MOTIF\t0\t1\t2\t3+"
header = "MOTIF"+SEP+"0"+SEP+"1"+SEP+"2"+SEP+"3+"+SEP+"MEAN"+SEP+"SUM"
lines=""
for i in range(1, size_col):

    print (df.columns[i])
    print ("Mean: %.3f motifs per region" % float(df[df.columns[i]].mean()))
    print ("Average region size: %.3f Kb" % (float(df['SIZE'].mean())/1000))
    print ("Mean: %.3f motifs per Kb" % ( (float(df[df.columns[i]].mean())) / (float(df['SIZE'].mean())/1000) )   )
    print ("Sum: "+str(df[df.columns[i]].sum()) + " motifs")
    print ("\n")
    #print df.iloc[i]
    categories = pandas.cut(df[df.columns[i]], bins, labels=group_names)
    #print categories
    df['categories'] = pandas.cut(df[df.columns[i]], bins, labels=group_names)
    df['scoresBinned'] = pandas.cut(df[df.columns[i]], bins)
    lines = lines+df.columns[i]+SEP
    for val, cnt in pandas.value_counts(df['categories'], sort=False).iteritems():
        line = lines+str(cnt)+SEP
    lines = line+str(df[df.columns[i]].mean())+SEP + \
        str(df[df.columns[i]].sum())+SEP
    lines = lines[:-1]+"\n"


# group
if args.combine:
    i = df.columns.get_loc(colname)
    print (df.columns[i])
    print ("Mean: "+str(df[df.columns[i]].mean()) + " motifs per region")
    print ("Sum: "+str(df[df.columns[i]].sum()) + " motifs")
    #print df.iloc[i]
    categories = pandas.cut(df[df.columns[i]], bins, labels=group_names)
    #print categories
    df['categories'] = pandas.cut(df[df.columns[i]], bins, labels=group_names)
    df['scoresBinned'] = pandas.cut(df[df.columns[i]], bins)
    lines = lines+df.columns[i]+SEP
    for val, cnt in pandas.value_counts(df['categories'], sort=False).iteritems():
        lines = lines+str(cnt)+SEP

    lines = lines+str(df[df.columns[i]].mean())+SEP + \
        str(df[df.columns[i]].sum())+SEP
    lines = lines[:-1]+"\n"

# TODO:Should be alphabetically sorted
#Sort alphabetically by motif
wlin=header
for line2 in sorted(lines.split("\n"), key=lambda line: line.split(",")[0]):
    if (line2 != ""):
        wlin=wlin+"\n"+line2
#print (wlin)
ou = open(outFile, "w")
ou.write(wlin)
ou.close()

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




startTime = time.time()



parser = argparse.ArgumentParser(description='Sorts and optionally removes duplicate entries in bed file.')
parser.add_argument('bed', type=str, help='bed file to process')
parser.add_argument('outBed', type=str, help='output file')
parser.add_argument('--uniq', action="store_true",help='Remove duplicate entries.' )

cs_utils.printProgString()
args = parser.parse_args()





bed=args.bed
out_bed=bed+".clean"
if args.outBed:
    out_bed=args.outBed
print ("Generating: "+out_bed)
if (args.uniq):
    print ("Removing duplicates")

cs_utils.cleanBed(bed,out_bed,args.uniq)




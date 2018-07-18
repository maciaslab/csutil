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
from Bio import motifs
import tempfile
import time
import random
import shutil
import sys
import cs_utils


startTime = time.time()

parser = argparse.ArgumentParser(description='Gets a TF binding motif from JASPAR and prints its degenerate consensus')
parser.add_argument('TF', type=str, help='TF to query')


cs_utils.printProgString()
args = parser.parse_args()
print "TF: "+args.TF

tempdir=tempfile.mkdtemp()
HEADERS = {'accept': 'application/json'}
URL = "http://jaspar.genereg.net/api/v1/matrix/?name="+args.TF
response = requests.get(URL, headers=HEADERS)
response_json_dict = response.json()
results=response_json_dict.get("results","")
for i in results:
	matrix=i.get("matrix_id","")
	print "MATRIX: "+matrix
	URL = "http://jaspar.genereg.net/api/v1/matrix/"+matrix+".pfm"
	response2 = requests.get(URL)
	e=open(tempdir+"/temp.pfm","w")
	for j in response2.text.splitlines():
		if j[0]==">":
			continue
		e.write(j+"\n")
	e.close()
	with open(tempdir+"/temp.pfm") as handle:
		m = motifs.read(handle, "pfm")
	print "CONSENSUS: "+m.degenerate_consensus+" / "+m.degenerate_consensus.reverse_complement()
	print "MATRIX:"
	print m.pwm
shutil.rmtree(tempdir)


#!python
import argparse
import urllib
import os
import zipfile
import progressbar
import requests
import json
from termcolor import colored
from tabulate import tabulate
import gzip
import shutil
import cs_utils
import glob

import sys  


dataPath = cs_utils.getDefault('dataPath')+"/encode/"

line = "--------------------"

# AAB
parser = argparse.ArgumentParser(description='Download encode data.')
subparsers = parser.add_subparsers(help='command', dest='command')
# A list command
search_parser = subparsers.add_parser('search', help='List contents')
search_parser.add_argument(
    'searchstring', action='store', help='Search encode')
search_parser.add_argument('--assembly', help='Filter by assembly')

list_parser = subparsers.add_parser(
    'list', help='List data in an encode experiment')
list_parser.add_argument('experiment', action='store',
                         help='An encode experiment, ex: ENCSR000AKS')
list_parser.add_argument('--assembly', help='Filter by assembly')
list_parser.add_argument('--fileType', help='Filter by fileType')

download_parser = subparsers.add_parser(
    'download', help='Download an encode datafile')
download_parser.add_argument(
    'datafile', action='store', help='An encode datafile, ex: ENCFF000BXQ')

fileinfo_parser = subparsers.add_parser(
    'fileinfo', help='Info about an encode datafile')
fileinfo_parser.add_argument(
    'datafile', action='store', help='An encode datafile, ex: ENCFF000BXQ')

local_parser = subparsers.add_parser(
    'local', help='List all downloaded encode files')

#parser.add_argument('--list', help='list available genomes',action="store_true")
parser.add_argument('--dataPath', help='set the dataPath')
cs_utils.printProgString()
args = parser.parse_args()


def listEncode(experiment):
    
    results = []
    print (colored("Checking experiment "+experiment+".", 'blue'))
    print (line)
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/biosample/"+experiment+"/?frame=object"
    response = requests.get(URL, headers=HEADERS)
    response_json_dict = response.json()
    #print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
    if (response_json_dict.get("@type","")[0] !="Experiment"):
        
        errormsg="ID "+experiment+" is not of the correct type (Experiment). It is of the '"+str(response_json_dict.get("@type","")[0])+"' type."
        print (colored(errormsg, 'red'))
        exit(1)

    print ("Description: "+response_json_dict.get("description", ""))
    print ("Assay: "+response_json_dict.get("assay_term_name", ""))
    print ("Date: "+response_json_dict.get("date_released", ""))
    print ("BioSample: "+response_json_dict.get("biosample_term_name", ""))
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/" + \
        response_json_dict["target"]+"/?frame=object"
    response3 = requests.get(URL, headers=HEADERS)
    response_json_dict3 = response3.json()
    #print json.dumps(response_json_dict3, indent=4, separators=(',', ': '))
    print ("Target: "+response_json_dict3["title"])
    #print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
    
    print ("\nFILES:")
    print (line)
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/biosample/"+experiment+"/?frame=embedded"
    response = requests.get(URL, headers=HEADERS)
    response_json_dict = response.json()
    #print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
    fileList = response_json_dict["files"]
    for item in fileList:
        
        results.append([item.get("accession", ""), item.get("assembly", ""), item.get("file_type", ""), item.get("output_type", "")])

        #print(item)
    print (tabulate(results, ["Accession", "Assembly",
                             "File type", "Output type"], tablefmt="simple"))




def searchEncode(searchstring):
    print (colored("Search:"+searchstring+".", "red"))
    print (line)
    assem = ""
    results = []
    if (args.assembly):
        assem = "&assembly="+args.assembly
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/search/?searchTerm="+searchstring.replace(
        " ", "+")+"&type=Experiment&assay_title=ChIP-seq&frame=object&limit=all"+assem
    response = requests.get(URL, headers=HEADERS)
    response_json_dict = response.json()
    #print response.text
    # if (response_json_dict["status"]=="error"):
    #	print "Error: "+response_json_dict["description"]
    #	return

    print (response_json_dict["notification"]+"\n")
    if (response_json_dict["notification"] != "Success"):
        return
    #print response_json_dict["facets"]["total"]
    graph = response_json_dict["@graph"]
    for item in graph:
        #print item
        assemblies = ""
        for a in item.get("assembly", []):
            if (assemblies != ""):
                assemblies = assemblies+","
            assemblies = assemblies+a
        results.append([item.get("accession", "").encode('utf-8'), assemblies.encode('utf-8'), item.get(
            "target", "").split("/")[2].encode('utf-8'), item.get("biosample_summary", "")])
        #print item.get("accession","")+"\t"+assemblies+"\t"+item.get("target","").split("/")[2]+"\t"+item.get("biosample_summary","")
    #print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
    #print (URL)
    
    print(tabulate(results, ["Accession", "Assemblies", "Target","Biosample"], tablefmt="rst"))
    return


def downloadEncode(datafile):
    
    fileinfoEncode(datafile)
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/files/"+datafile+"/?frame=object"
    response = requests.get(URL, headers=HEADERS)
    response_json_dict = response.json()
    if (response_json_dict["status"] == "error"):
        print ("Error: "+response_json_dict["description"])
        return
    #print json.dumps(response_json_dict, indent=4, separators=(',', ': '))

    remotePath = "https://www.encodeproject.org"+response_json_dict["href"]

    filename = datafile+"."+response_json_dict["file_format"]
    if (remotePath[-3:] == ".gz"):
        filename = filename+".gz"
    filePath = dataPath+filename
    try:
        if not(os.path.exists(dataPath)):
            os.makedirs(dataPath)
    except OSError:

        print( "Note: Directory already exists (or not writable).")
    cs_utils.downloadFile(remotePath, filePath)
    if (remotePath[-3:] == ".gz"):
        print ("Gzipped file, unzipping")
        with open(filePath[:-3], 'wb') as f_out, gzip.open(filePath, 'rb') as f_in:
            shutil.copyfileobj(f_in, f_out)
        os.remove(filePath)
    return


def fileinfoEncode(datafile):
    
    print (colored("Checking "+datafile+".", "blue"))
    print (line)
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/files/"+datafile+"/?frame=object"
    response = requests.get(URL, headers=HEADERS)
    response_json_dict = response.json()
    #print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
    if (response_json_dict["status"] == "error"):
        print ("Error: "+response_json_dict["description"])
        return
    if (response_json_dict.get("@type","")[0] !="File"):
        
        errormsg="ID "+datafile+" is not of the correct type (File). It is of the '"+str(response_json_dict.get("@type","")[0])+"' type."
        print (colored(errormsg, 'red'))
        exit(1)
    #print response_json_dict

    print ("Accession: "+response_json_dict.get("accession", ""))
    print ("Dataset: "+response_json_dict.get("dataset", "").split("/")[2])
    print ("Assembly: "+response_json_dict.get("assembly", ""))
    print ("Type: "+response_json_dict.get("output_type", ""))
    print ("File type: "+response_json_dict.get("file_type", ""))
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/" + \
        response_json_dict["dataset"]+"/?frame=object"
    response2 = requests.get(URL, headers=HEADERS)
    response_json_dict2 = response2.json()
    print ("Description: "+response_json_dict2.get("description", ""))
    print ("Assay: "+response_json_dict2.get("assay_term_name", ""))
    print ("Date: "+response_json_dict2.get("date_released", ""))
    print ("BioSample: "+response_json_dict2.get("biosample_term_name", ""))
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/" + \
        response_json_dict2["target"]+"/?frame=object"
    response3 = requests.get(URL, headers=HEADERS)
    response_json_dict3 = response3.json()
    #print json.dumps(response_json_dict3, indent=4, separators=(',', ': '))
    print ("Target: "+response_json_dict3["title"])
    return

def localEncode():

    results=[]
    for file in glob.glob(dataPath+"/*"):
        filename=os.path.basename(file)
        a=((os.path.splitext(filename))[0])
        results.append([filename]+fileinfoEncodeMini(a))
    print ("List of files downloaded to " + dataPath)
    print (line)
    print (tabulate(results, ["Filename","Accession", "Dataset", "Assembly",
                             "File type","Output Type","Description"], tablefmt="rst"))
def fileinfoEncodeMini(datafile):
    
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/files/"+datafile+"/?frame=object"
    response = requests.get(URL, headers=HEADERS)
    response_json_dict = response.json()
    #print json.dumps(response_json_dict, indent=4, separators=(',', ': '))
    if (response_json_dict["status"] == "error"):
        print ("Error: "+response_json_dict["description"])
        return
    HEADERS = {'accept': 'application/json'}
    URL = "https://www.encodeproject.org/" + \
        response_json_dict["dataset"]+"/?frame=object"
    response2 = requests.get(URL, headers=HEADERS)
    response_json_dict2 = response2.json()
    return [response_json_dict.get("accession", "").encode('utf-8'),response_json_dict.get("dataset", "").split("/")[2].encode('utf-8'), response_json_dict.get("assembly", "").encode('utf-8'), response_json_dict.get("file_type", "").encode('utf-8'), response_json_dict.get("output_type", "").encode('utf-8'),response_json_dict2.get("description","").encode('utf-8')]


if args.dataPath:
    dataPath = args.dataPath+"/encode"

command = args.command

if command == "search":
    searchEncode(args.searchstring)

if command == "list":
    listEncode(args.experiment)

if command == "download":
    downloadEncode(args.datafile)


if command == "fileinfo":
    fileinfoEncode(args.datafile)

if command == "local":
    localEncode()
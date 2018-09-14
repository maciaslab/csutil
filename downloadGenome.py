#!python
import argparse
import os
import urllib
from termcolor import colored
import progressbar
import xmltodict
import cs_utils
import requests
import tabulate
import tarfile
import shutil
import gzip
import re
import glob


parser = argparse.ArgumentParser(description='Download genomes from ucsc.')
parser.add_argument('genome', type=str, nargs='?', help='genome to download')
parser.add_argument('--list', help='list available genomes',
                    action="store_true")
parser.add_argument('--local', help='list already downloaded genomes',
                    action="store_true")                    
parser.add_argument('--dataPath', help='set the dataPath')

cs_utils.printProgString()
args = parser.parse_args()

ok_symbol="✓"

def listGenomes():
    
    print ("List of supported genomes:\n")
    print (tabulate.tabulate(getGenomeList(),["Assembly","Local","Description"],tablefmt="rst"))
    
    return

def getGenomeList():
    das_url = "http://genome.ucsc.edu/cgi-bin/das/dsn"
    response = requests.get(das_url)
    mydict = xmltodict.parse(response.text)
    genome_list = []
    for genome in mydict['DASDSN']['DSN']:
            genome_name=genome['SOURCE']['@id']
            genomePath = dataPath+"/genomes/"+genome_name
            genome_local=""
            if (os.path.isdir(genomePath)):
                genome_local=ok_symbol
            genome_list.append([genome['SOURCE']['@id'],genome_local, genome['DESCRIPTION']])
    return genome_list

def CheckUrls(url1,url2):
    retcode=requests.head(url1)
    if retcode.status_code==200:
        return ([True,url1])
    retcode=requests.head(url2)
    if retcode.status_code==200:
        return ([False,url2])
    return([False,None])
def downloadGenome(genome):
    
    #then concatenate with cs_utils.concatenateFiles(["1.fasta","2.fasta"],"hg19.fasta")
    #Gene positions
    #http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/refGene.txt.gz -> genomes/genomes/hg19/refGene.txt
    #Chromosome sizes
    #http://hgdownload.cse.ucsc.edu/goldenpath/hg19/bigZips/hg19.chrom.sizes-> genomes/sizes/hg19/hg19.chrom.sizes
    #This is included in the distrbution

    
    genomes=[]
    for item in getGenomeList():
        genomes.append(item[0])
    if not(genome in genomes):
        print (colored("Error, assembly '"+genome+ "' not found",'red'))
        exit(1)
    print ("Downloading "+genome+".")

    
    genomePath = dataPath+"/genomes/"+genome
    genome_url="http://hgdownload.cse.ucsc.edu/goldenpath/"+genome+"/bigZips/chromFa.tar.gz"
    genome_url_2="http://hgdownload.cse.ucsc.edu/goldenpath/"+genome+"/bigZips/"+genome+".fa.gz"
    
    chromsizes_url="http://hgdownload.cse.ucsc.edu/goldenpath/"+genome+"/bigZips/"+genome+".chrom.sizes"
    chromsizes_local=genomePath+"/"+genome+".chrom.sizes"
    refgene_url="http://hgdownload.cse.ucsc.edu/goldenpath/"+genome+"/database/refGene.txt.gz"
    refgene_local=genomePath+"/refGene.txt"
    
    is_multi,genome_url=CheckUrls(genome_url,genome_url_2)
    genome_local=genomePath+"/"+genome+".fa.gz"
    if (is_multi):
        genome_local=genomePath+"/"+"chromFa.tar.gz"
    try:
        os.makedirs(genomePath)
    except OSError:
        print ("Directory already exists or not writable.")
    print ("Downloading chromosome sizes \nfrom: "+chromsizes_url+" \nto "+chromsizes_local)

    

    cs_utils.downloadFile(chromsizes_url, chromsizes_local)
    print ("Downloading gz \nfrom: "+genome_url+" \nto "+genome_local)
    cs_utils.downloadFile(genome_url, genome_local)
    if (is_multi):
        print ("Expanding file...")
        tf=tarfile.open(name=genome_local,mode="r")
        tf.extractall(path=genomePath+"/temp")
        f = open(chromsizes_local, 'r')
        fastalist=[]
        for line in f.readlines():
                spline = line.split()
                chr_id=(spline[0].split("_")[0][3:])
                filename=genomePath+"/temp/"+spline[0]+".fa"
                filename2=genomePath+"/temp/"+chr_id+"/"+spline[0]+".fa"
                #print (filename+" "+filename2)
                if (os.path.isfile(filename)): 
                    fastalist.append(filename)
                elif (os.path.isfile(filename2)):
                    fastalist.append(filename2)
        #print (fastalist)
        print ("Combining file...")
        cs_utils.concatenateFiles(fastalist,genomePath+"/"+genome+".fasta")
        shutil.rmtree(genomePath+"/temp")
        os.remove(genome_local)

    else:
        print ("Gzipped file, unzipping")
        with open(genome_local[:-3]+"sta", 'wb') as f_out, gzip.open(genome_local, 'rb') as f_in:
            shutil.copyfileobj(f_in, f_out)
        os.remove(genome_local)
    
    print ("Downloading gz \nfrom: "+refgene_url+" \nto "+refgene_local+".gz")
    cs_utils.downloadFile(refgene_url, refgene_local+".gz")
    with open(refgene_local, 'wb') as f_out, gzip.open(refgene_local+".gz", 'rb') as f_in:
            shutil.copyfileobj(f_in, f_out)


def localGenomes():
    
    genomePath=dataPath+"genomes"
    genomes=getGenomeList()
    print ("List of files downloaded to " + genomePath)
    results=[]
    for file in glob.glob(genomePath+"/*"):
        filename=os.path.basename(file)
        description="Unknown"
        for item in genomes:
            if (item[0] == filename):
                description= item[2]
        size=cs_utils.humanBytes(cs_utils.get_size(file))
        results.append([filename,description,size])

        
    print (tabulate.tabulate(results, ["Genome","Description","Size"], tablefmt="rst"))
    totalSize=size=cs_utils.humanBytes(cs_utils.get_size(genomePath))
    print( "Total Size: "+totalSize)


dataPath = cs_utils.getDefault('dataPath')+"/genomes/"
if args.dataPath:
	dataPath=args.dataPath+"/genomes/"



if args.list:
    listGenomes()

if args.local:
    localGenomes()

if args.genome:
    downloadGenome(args.genome)

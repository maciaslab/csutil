#!python
# coding: utf-8


import cs_utils
import pip
import os

cs_utils.printProgString()

tests=0
passed_tests=0


print("Checking needed packages:\n")
err_=False
required_pkgs = ['biopython', 'tabulate','termcolor','natsort','pandas','progressbar','regex','requests','xmltodict']
installed_pkgs = [pkg.key for pkg in pip.get_installed_distributions()]

for package in required_pkgs:
    if package not in installed_pkgs:
        print ("ERROR: "+package +" not found.")
        err_=True
    else:
         print (package +" found.")
tests=tests+1
if (err_):
    print "\nInstall missing packages with:\npip install packagename\n"
if not(err_):
    passed_tests=passed_tests+1

#Test bedtools
print("\n")
tests=tests+1
bedtools_exec=cs_utils.getbedtools(verbose=True,quit_err=False)
if (bedtools_exec != None):
    passed_tests=passed_tests+1


if (os.environ.get('GENOME_DATAPATH') == None):
        print ("\nEnvironment variable GENOME_DATAPATH is not set.\nFor more info check the installation instructions.")

print("\n")
print "Tests passed %i / %i" % (passed_tests, tests)
if (passed_tests == tests):
    print "Installation is correct."
else:
    print "There are errors."

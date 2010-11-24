#! /Library/Frameworks/Python.framework/Versions/Current/bin/python
import sys
import immgen
import logging

log = logging.getLogger('immgen')
log_filename = "/ifs/home/c2b2/cw_lab/md2954/Data/immgen.log" 
logging.basicConfig(filename=log_filename, level=logging.DEBUG)


def usage():
	u = """\n\n python preprocess_setup root_folder GEOid
	
	Sets up a filesystem and downloads the necessary file for subsequent
	preprocessing by the aroma package (done elsewhere)
	
	Parameters
	==========
	root_folder : path
		where your data is stored (or will be stored)
	GEOid : GEO accession ID (optional)
		GEO accession ID of the data set you'd like to preprocess
	
	Returns
	=======
	A fully populated aroma file system tree
	
	Notes
	=====
	The default GEOid is the immgen data set GSE15907.
	
	WARNING : you need to populate 
	<root_folder>anotationData/chipTypes/<chip_folder>/ manually!
	
	Example
	=======
	python preprocess_setup.py /Users/mike/Data/Test
	"""
	print u

try:
	root_folder = sys.argv[1]
	if root_folder in ["-h","--help"]:
		usage()
		sys.exit()
except IndexError:
	usage()
	raise ValueError("you must specify a root folder")

try:
	GEOid = sys.argv[2]
except IndexError:
	immgen.setup_preprocessing(root_folder)
else:
	immgen.setup_preprocessing(root_folder,GEOid)

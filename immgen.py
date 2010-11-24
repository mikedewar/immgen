import os
import logging
log = logging.getLogger('immgen')
try:
    import rpy2.robjects as robjects
except ImportError:
    log.warn("AAAH no rpy2 - hope you don't need it! (i.e. you're running preprocess_setup.py)")
import sys
import urllib


# A set of tools for processing immgen data. Makes heavy use of the
# aroma.affymetrix R package.
#
# Mike Dewar @ WigginsGroup, Columbia, NY 2010

def get_folder_structure(root_folder,GEOid):
    """
    Parameters
    ----------
    root_folder : string
        path to the root of your folder structure
    GEOid : string
        GEO acceision ID
    
    Returns
    -------
    p : list
        a list of the paths required for the aroma.affy R package
    """
    join = os.path.join
    p = []
    p += [join(root_folder, "annotationData")]
    p += [join(root_folder, "rawData")]
    p += [join(p[0], "chipTypes")]
    p += [join(p[0], "samples")]
    p += [join(p[2], "MoGene-1_0-st-v1")]
    p += [join(p[1], GEOid)]
    p += [join(p[5], "MoGene-1_0-st-v1")]
    p += [join(root_folder, "userData")]
    p += [join(p[7], GEOid)]
    return [root_folder]+p

def create_folders(folder_structure):
    """
    Parameters
    ==========
    folder_structure : list
        a list of paths that you'd like to build (probably generated using
        get_folder_structure in this module)
    """
    log.info('creating aroma.affymetrix folder structure')
    for p in folder_structure:
        try:
            if not os.path.exists(p):
                os.mkdir(p)
        except OSError:
            print "trouble with directory: %s"%p
            raise

def validate_folders(folder_structure):
    """
    validates the folder structure that you're using for the aroma.affymetrix
    package.
    
    Parameters
    ==========
    folder_structure : list
        a list of paths that you'd like to check (probably generated using
        get_folder_structure in this module)
    """
    log.info('validating aroma.affymetrix folder structure')
    for p in folder_structure:
        assert os.path.isdir(p)
    return p

def validate_data(root_folder,GEOid):
    """
    checks to make sure we have at least one cel file where we should have data
    """
    ls = os.listdir(os.path.join(root_folder,"rawData",GEOid,"MoGene-1_0-st-v1",))
    assert any([f.lower().endswith('.cel') for f in ls])

def validate_annotation(root_folder,chiptype="MoGene-1_0-st-v1"):
    """
    checks to make sure we've got the appropriate CDF file
    """
    assert root_folder
    log.debug('root folder in "validate annotation": %s'%root_folder)
    p = os.path.join(
            root_folder, 
            '/annotationData/chipTypes/MoGene-1_0-st-v1/MoGene-1_0-st-v1,r3.cdf'
        )
    log.info('asserting that %s exists'%p)
    assert os.path.isfile(p)
    
def download_data(root_folder,GEOid="GSE15907",raw_filename="GSE15907_RAW.tar"):
    params = urllib.urlencode({
        "mode": "raw",
        "acc": GEOid,
        "db": raw_filename,
        "is_ftp": "true"
    })
    url = "http://www.ncbi.nlm.nih.gov/projects/geo/query/acc.cgi?%s"
    # download the file
    log.info("downloading raw data, could take a while..")
    raw_file_path = os.path.join(root_folder,raw_filename)
    urllib.urlretrieve(url%params,raw_file_path)
    return raw_file_path

def download_annotation(root_folder,GEOid="GSE15907",chiptype="MoGene-1_0-st-v1"):
    log.info('downloading annotation file')
    if chiptype=="MoGene-1_0-st-v1":
        mouse_url = "http://bioinf.wehi.edu.au/folders/mrobinson/CDF/MoGene-1_0-st-v1,r3.cdf"
        cdf_file_path = os.path.join(
            root_folder, 
            'annotationData/chipTypes/MoGene-1_0-st-v1/MoGene-1_0-st-v1,r3.cdf'
        )
        log.info('trying to retrieve %s'%mouse_url)
        log.info('will store it in %s'%cdf_file_path)
        try:
            urllib.urlretrieve(mouse_url,cdf_file_path)
        except IOError:
            log.error('could not download %s'%mouse_url)
            raise
    else:
        raise NotImplementedError
    
def distribute_data(root_folder, raw_file_path, GEOid="GSE15907"):
    # move it into the right spot
    new_raw_file_path = os.path.join(
        root_folder,
        "rawData",
        GEOid,
        "MoGene-1_0-st-v1",
        os.path.split(raw_file_path)[1]
    )
    os.system("mv %s %s"%(raw_file_path,new_raw_file_path))
    # untar
    os.system(
        "tar -C %s -xvf %s"%
        (os.path.split(new_raw_file_path)[0], new_raw_file_path)
    )
    # then unzip all the files individually (ugh!)
    zipped_files = os.path.join(root_folder,"rawData",GEOid,"MoGene-1_0-st-v1","*.%s")
    os.system('gunzip '+zipped_files%"CEL.gz")
    os.system('gunzip '+zipped_files%"cel.gz")


def setup_preprocessing(root_folder,GEOid="GSE15907",raw_file_present=True):
    """
    This sets up a system for subsequent preprocessing of cel files by aroma.
    If your system doesn't support rpy2, then you can use this to download the
    immgen files and set up the aroma file system, then use the 
    preprocess_rscript.r to actually do the preprocessing. In fact, that script
    calls a python script whcih calls this function by default.
    
    Parameters
    ==========
    root_folder : string
        path to the root folder of your data directory structure
    GEOid : string
        the GEO accession ID. Default is the standard immgen set
    raw_file_present : bool (False)
        you've already downloaded the file, and put it in the root_folder?
        Then set this to true and we won't try and download it again.
    
    Notes
    =====
    Everything generated by this script is stored in
    `<root_folder>/userData/<GEOid>/`
    """
    log.info("using %s as the root folder"%root_folder)
    # sort out folders
    folder_structure = get_folder_structure(root_folder,GEOid)
    try:
        validate_folders(folder_structure)
        log.info('folder structure validated')
    except AssertionError:
        log.info('creating folder structures')
        create_folders(folder_structure)
        log.info("folder structure created!")
    
    try:
        validate_data(root_folder,GEOid)
        log.info('data validated')
    except AssertionError:
        if raw_file_present:
            ls = os.listdir(root_folder)
            fname = os.path.abspath(
            ls[[f.lower().endswith(".tar") for f in ls].index(True)]
            )
            log.info("using raw file: %s"%fname)
        else:
            log.info("no raw file present: downloading data")
            fname = download_data(root_folder)
            log.info("data downloaded - running the aroma preprocessing")

        log.info('distributing data')
        distribute_data(root_folder,fname)
    
    try:
        validate_annotation(root_folder)
        log.info('annotation validated')
    except AssertionError:
        log.info('downloading annotation')
        download_annotation(root_folder)
        log.info('annotation downloaded')


def preprocess(root_folder,GEOid="GSE15907",outfile="immgen.data",raw_file_present=False):
    """
    preproceses the CEL files using aroma.affymetrix and bits of Bioconductor
    
    Parameters
    ==========
    root_folder : string
        path to the root folder of your data directory structure
    GEOid : string
        the GEO accession ID. Default is the standard immgen set
    outfile : string
        name of the outfile you'd like to generate (default: "immgen.data")
    raw_file_present : bool (False)
        you've already downloaded the file, and put it in the root_folder?
        Then set this to true and we won't try and download it again.
    
    Notes
    =====
    Everything generated by this script is stored in
    `<root_folder>/userData/<GEOid>/`
    """
    # sort out folders
    folder_structure = get_folder_structure(root_folder,GEOid)
    try:
        validate_folders(folder_structure)
        log.info('folder structure validated')
    except AssertionError:
        log.info('creating folder structures')
        create_folders(folder_structure)
        log.info("folder structure created!")
    
    try:
        validate_data(root_folder,GEOid)
        log.info('data validated')
    except AssertionError:
        if raw_file_present:
            ls = os.listdir(root_folder)
            fname = os.path.abspath(
                ls[[f.lower().endswith(".tar") for f in ls].index(True)]
            )
            log.info("using raw file: %s"%fname)
        else:
            log.info("no raw file present: downloading data")
            fname = download_data(root_folder)
            log.info("data downloaded - running the aroma preprocessing")
        
        log.info('distributing data')
        distribute_data(root_folder,fname)
    
    try:
        validate_annotation(root_folder)
    except AssertionError:
        download_annotation(root_folder)
    
    # 'source' the preprocess file, which contains all the preprocessing
    # functions
    robjects.r("""source('preprocess.r')""")
    # run the preprocessing script with the properly formed arguments
    log.info("preprocessing")
    join = lambda x: os.path.join(root_folder,"userData",GEOid,x)
    summary_file = join("gene_summary.data")
    args = (
        root_folder,
        summary_file,
        GEOid
    )
    robjects.r("""immgen.preprocess("%s","%s",GEOid="%s")"""%args)
    # form the symbol file, which we need in order to output and expression
    # set
    symbol_file = join("probes2symbols.data")
    if not os.path.exists(symbol_file):
        log.info("forming the symbol file")
        robjects.r("""immgen.form_symbol_file("%s")"""%symbol_file)
    # form the expression set
    args = (
        summary_file,
        symbol_file,
        join(outfile),
    )
    robjects.r("""immgen.form_expression_set("%s","%s","%s")"""%args)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,level=logging.INFO)
    root_folder = "/Users/mike/Data/Immgen2"
    preprocess(root_folder)
    

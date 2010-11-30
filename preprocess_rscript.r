# this script specifies the necessary folders for the immgen preprocessing script.
# this assumes you've already run preprocess_setup.py which sets up the folder 
# structure for aroma

source('preprocess.r')

root_folder = "/ifs/home/c2b2/cw_lab/md2954/Data/immgen"
GEOid = "GSE15907"
summary_file = "/ifs/home/c2b2/cw_lab/md2954/Data/immgen/userData/GSE15907/gene_summary.data"
symbol_file = "/ifs/home/c2b2/cw_lab/md2954/Data/immgen/userData/GSE15907/probes2symbols.data"
out_file = "/ifs/home/c2b2/cw_lab/md2954/Data/immgen/userData/GSE15907/immgen.data"


immgen.preprocess(root_folder,summary_file,GEOid=GEOid)
#immgen.form_symbol_file(symbol_file)
#immgen.form_expression_set(summary_file,symbol_file,out_file)

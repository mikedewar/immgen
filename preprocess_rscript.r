# this script calls python as system calls, rather than relying on rpy2
# you'll need to set all the paths and whatnot by hand
# look at immgen.py for details. This is just a hack really for c2b2

system("python preprocess_setup.py ~/Data/immgen")
source('preprocess.r')

root_folder = "~/Data/immgen"
GEOid = "GSE15907"
summary_file = "~/Data/immgen/userData/GSE15907/gene_summary.data"
symbol_file = "~/Data/immgen/userData/GSE15907/probes2symbols.data"
out_file = "~/Data/immgen/userData/GSE15907/immgen.data"


immgen.preprocess(root_folder,summary_file,GEOid=GEOid)
immgen.form_symbol_file(symbol_file)
immgen.form_expression_set(summary_file,symbol_file,out_file)
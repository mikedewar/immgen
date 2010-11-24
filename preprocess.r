# load the necessary R libraries
library(aroma.affymetrix)
library(Biobase)
library(GEOquery)
library(mogene10sttranscriptcluster.db)
library(AffyExpress)

immgen.preprocess <- function (root_folder, outfile,GEOid="GSE15907"){
    print("preprocessing")
	# change to the root folder of the data set
	setwd(root_folder)
	# form data (cel) and platform (cdf) objects
	cdf <- AffymetrixCdfFile$byChipType('MoGene-1_0-st-v1',tags='r3')
	cs <- AffymetrixCelSet$byName(GEOid,cdf=cdf)
	# background correction
	bc <- RmaBackgroundCorrection(cs)
	csBC <- process(bc,verbose=verbose)
	# normalise
	qn <- QuantileNormalization(csBC, typesToUpdate="pm")
	csN <- process(qn, verbose=verbose)
	# proble level model
	plm <- RmaPlm(csN)
	fit(plm,verbose=verbose)
	# extract data from the probe level model
	ces <- getChipEffectSet(plm)
	gene_summary <- extractMatrix(ces,returnUgcMap=TRUE)
	# transform to a log scale
	gene_summary <- log2(gene_summary)
	#add the unit names and convert to dataframe
	rownames(gene_summary) <- getUnitNames(cdf,
		units=attr(gene_summary,'unitGroupCellMap')[,'unit']
	)
	gene_summary_df = as.data.frame(gene_summary)
	save(gene_summary_df,file=outfile)
}

immgen.form_symbol_file <- function(outfile){
    print("forming symbol file")
	# get the platform data from GEO
	gpl <- Table(getGEO('GPL6246', destdir="."))
	# retrieve SYMBOLs from the mogene db
	probeID2Symbol <- mogene10sttranscriptclusterSYMBOL
	mapped_probes <- mappedkeys(probeID2Symbol)
	probe2symbol <- as.list(probeID2Symbol[mapped_probes])[gpl$ID]
	probe2symbol <- probe2symbol[!is.na(names(probe2symbol))]
	save(probe2symbol,file=outfile)
}

immgen.form_ensembl_file <- function(outfile){
    print("forming ensembl file")
	# get the platform data from GEO
	gpl <- Table(getGEO('GPL6246', destdir="."))
	# retrieve SYMBOLs from the mogene db
	probeID2ensembl <- mogene10sttranscriptclusterENSEMBL
	mapped_probes <- mappedkeys(probeID2ensembl)
	probe2ensembl <- as.list(probeID2ensembl[mapped_probes])[gpl$ID]
	probe2ensembl <- probe2ensembl[!is.na(names(probe2ensembl))]
	save(probe2ensembl,file=outfile)
}

immgen.form_expression_set <- function(gene_summary_file, probe2symbol_file,
	outfile, GEOid="GSE15907", phenotype_file=NULL){
	print("forming expression set")
	# load the preprocessed file and the symbol file
	load(gene_summary_file) #gene_summary_df
	load(probe2symbol_file) #probe2symbol
	# convert to a matrix and sort out the sample names
	splitnames <- strsplit(colnames(gene_summary_df), '_')
	colnames(gene_summary_df) <- sapply(splitnames, '[', 1)
	# throw away unlabelled probes
	symbols <- probe2symbol[rownames(gene_summary_df)]
	na_label_index <- is.na(names(symbols))
	assay_data <- as.matrix(gene_summary_df[!na_label_index,])
	# generate a feature data object using AnnotateDataFrame
	assay_symbols = as.data.frame(as.matrix(symbols[!na_label_index]))
	colnames(assay_symbols) <- "symbol"
	meta_data <- data.frame(c("gene symbol from mogene10sttranscriptcluster.db"))
	colnames(meta_data) <- c("labelDescription")
	featureData <- new("AnnotatedDataFrame",
		data = assay_symbols,
		varMetadata = meta_data
	)
	# generate a phenotype data object using AnnotateDataFrame
	if (!is.null(phenotype_file)){
		phen <- read.csv(phenotype_file)
		colnames(phen) <- c("4+","8+")
		meta_data <- data.frame(c("presence of CD4+","presence of CD8+"))
		colnames(meta_data) <- c("labelDescription")
		phenoData <- new("AnnotatedDataFrame", 
			data = phen[colnames(assay_data),],
			dimLabels = c("sample","phenotype"),
			varMetadata = meta_data
		)
		# generate an expression set
		immgen <- new("ExpressionSet", 
			phenoData = phenoData,
			featureData = featureData,
			exprs = assay_data
		)
	} else {
		# generate an expression set, using the default phenotype labels from
		# the data stored on GEO
		# generate labels for each experiment
		g <- getGEO(GEOid,destdir=".")[[1]]
		# exp_names are the name of each array like "GSM...."
		exp_names <- colnames(gene_summary_df)
		# exp labels are the description of the array like "Thymus CD4+..."
		phen_markers = sub(
			"phenotype markers: ",
			"",
			pData(g)$characteristics_ch1.5
		)
		excl_markers = sub(
			"exclusion markers: ",
			"",
			pData(g)$characteristics_ch1.3
		)
		description <- gsub("#\\d","",pData(g)$description)
		classnames = 
		#data <- data.frame(lapply(classnames,function(c){c==description}))
		#colnames(data) <- classnames
		#rownames(data) <- exp_names
		data <- data.frame(phen_markers, excl_markers, description, 
			pData(g)$title
		)
		colnames(data) <- c('phenotype','exclusion','description','title')
		rownames(data) <- exp_names
		phenoData <- new("AnnotatedDataFrame", 
			data = data,
			dimLabels = c("sample","label_type"),
			varMetadata = data.frame(colnames(data))
		)
		immgen <- new("ExpressionSet",
			phenoData = phenoData,
			featureData = featureData,
			exprs = assay_data
		)
	}
	# print the expression set
	print(immgen)
	# save the expression set
	save(immgen, file=outfile)
}


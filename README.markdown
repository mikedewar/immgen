# preprocess_immgen_data

This project aims to wrap up a set of tools using Python and R (Bioconductor and aroma.affymetrix) in order to easily process data generated using the IMMGEN protocol. 

For more information about the Immunological Genome Project see their website at [http://www.immgen.org](http://www.immgen.org)

The raw data sets are made available via the GEO data base, and can be found using the GEO accession ID [GSE15907]( http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE15907)

This project is part of the NIH Nanomedicine Center for Mechanobiology. Code written in the [Wiggins Group at Columbia University](http://www.columbia.edu/~chw2/).

## INSTALLATION

This will only work on a UNIX computer (and it's only been actually tested on OSX). It will definitely NOT work on Windows.

You'll need a special R package for this to work:

* [aroma.affymetrix](http://www.aroma-project.org/)

which allows you to normalise so many arrays in finite memory (i.e. your laptop).

You'll need the following things from [Bioconductor](http://www.bioconductor.org/)

* Biobase
* GEOquery
* mogene10sttranscriptcluster.db
* AffyExpress

You'll also need one non-standard python package:

* [rpy2](http://rpy.sourceforge.net/rpy2.html)

Then you can either use the `immgen` python package or the command line script `preprocess_immgen_data`

## USAGE

run `preprocess_immgen_data` --help for usage instructions.

## DESCRIPTION

This program uses Python to:

* lay out a directory structure according to the aroma project
* download the IMMGEN tarball (this is, at time of writing, 2GB) from GEO
* move it to the required destination, un-tar it, and then unzip the resulting gzipped CEL files. 

If you've already done all this manually, then the above is skipped, unless there's something wrong with the cel files, or the directory structure, in which case an error will be issued.

Then, via Rpy2, this program uses the aroma package in R to perform:

* background correction
* quantile normalisation
* probe level modelling
* log2 transformation

all this is in the `immgen.preprocess` function in the `preprocess.r` file. Then Bioconductor `ExpressionSet` objects are formed and saved in the `userData` folder in the data folder you specified. 

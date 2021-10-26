# HSBCstatementtoCSV
This is a small python script to convert HSBC statements into a csv file

Input parameter is the location of the PDF file.

use:

> python3 PDFplumb.py file_path

For multiple files, replace PDF/* with the location of your PDF-s within a single file
> for line in ls -d PDF/*; do python3 PDFplumb.py $line; done

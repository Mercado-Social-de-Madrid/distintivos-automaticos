#!/bin/bash

# Thank you, ChatGPT!

# set the directory where your PDF files are located
PDF_DIR=./distintivos

# loop through all subdirectories of PDF_DIR
find "$PDF_DIR" -type f -name "*.pdf" -print0 | while IFS= read -r -d $'\0' pdf_file; do
    # create the PNG file name by replacing the extension of the PDF file with ".png"
    png_file="${pdf_file%.pdf}.png"

    # convert the PDF file to a PNG file using the convert command from ImageMagick
    convert -density 300 -quality 100 -colorspace sRGB "$pdf_file" "$png_file"
done

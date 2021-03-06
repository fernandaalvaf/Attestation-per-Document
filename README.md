# ATTESTATION PER DOCUMENT

Attestation per document is a python webscraper used for getting information about texts from Trismegistos and Papyri.info.
It scrapes information from both databases and saves it to a .pdf file. In the resulting document you will find:
- A list of people attested in the document with Name, TM per id, Attestation id, attestation line, action.
- Title (from papyri.info)
- TM id
- Identification of the main publication
- Date
- Summary
- Text in Greek

# ONLY ATTESTATIONS 

This is a separate script that contains only the part of the code of the main program which is dedicated to get the attestations list per document. It works in the same way described in this file (See section "How to use:"), but the resulting .pdf file only contains a raw list of attestations.

# Setup

You should have the .py and the "newathu5_7.ttf" in the same folder before running the code. The newathu5_7 is the font used in the .pdf file which is generated.

This project was created with Python 3.

Before running the code you have to install the following libraries:
requests,
bs4,
reportlab,
termcolor.


# How to use

After the Setup is done, run the code. It will ask you to input the TMid of the text. 
It will save the .pdf file and ask if you wish to run the code again (type 'y') or exit (type 'n').

# Acknowledgements

As this code uses Trismegistos' database, you have to make appropriate reference to them in any publications making use of results generated through Trismegistos via this program. You can do so as specified on www.trismegistos.org/about_how_to_cite.


# License

MIT License

Copyright (c) 2021 Fernanda Alvares Freire

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

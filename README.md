# ATTESTATION PER DOCUMENT

Attestation per document is a python (python3) webscraper used for getting information about texts from Trismegistos and Papyri.info.
It scrapes information from both databases and saves it to a .pdf file. In the resulting document you will find:
- A list of people attested in the document with Name, TM per id, Attestation id, attestation line, action.
- Title (from papyri.info)
- TM id
- P. Cairo Zen. identification
- Date
- Summary
- Text in Greek

# Setup

You should have the .py and the "newathu5_7.ttf" in the same folder before running the code. The newathu5_7 is the font used in the .pdf file which is generated.

Before running the code you have to install the following libraries:
requests,
bs4,
reportlab,
termcolor.

# How to use

After the Setup is done, run the code. It will ask you to input the TMid of the text. You have to type "TM" and the id of the text.
It will save the .pdf file and ask if you wish to run the code again (type 'y') or exit (type 'n').

# Acknowledgements

As this code uses Trismegistos' database, you have to make appropriate reference to them in any publications making use of results generated through Trismegistos via this program. You can do so as specified on www.trismegistos.org/about_how_to_cite.

# Project Status

The code currently supports only entries belonging to the P. Cairo Zen. series. This will be updated in the future to include other texts.

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

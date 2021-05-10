#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import subprocess
import requests
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import unicodedata
from codecs import StreamRecoder
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from urllib.request import urlopen
import os
from urllib.request import urlopen
from termcolor import colored

    # Function to check for the row containing the data:


def checktargetdata(pattern, text):
    match = re.search(pattern, str(text))
    return bool(match)


run = True

while run:

    print("Hi, this program allows you to save the attestation list of papyri which are available \n"
          "in Trismegistos.")

    Pub = input("Input the TM id of the text:")



    # The user might type the id with TM or without it (i.e.: TM 1013 or just 1013), this section of the code identifies
    # the input and separates the numerical id to the initials TM.

    TMid_pattern = re.compile(r"(\s?[tT][mM]\s?)(\d+)")
    pub_input = checktargetdata(TMid_pattern, Pub)

    if pub_input is False:
        TMid = Pub
        full_TM = 'TM ' + TMid
    elif pub_input is True:
        TMid_match = TMid_pattern.finditer(Pub)
        for match in TMid_match:
            TMid = match.group(2)
            full_TM = Pub


    # Now we need to build the TM URL

    TM_baseURL = "https://www.trismegistos.org/text/"
    TMURL = TM_baseURL + TMid


   # Parsing the TM html

    TM_HTML = urlopen(TMURL).read()
    TM_r = requests.get(TMURL)
    TM_soup = BeautifulSoup(TM_r.text, features="html.parser")

    pattern_noresults = re.compile(r'no results for this number in TM')

    # Finding the DDbDP link

    noresultscheck = checktargetdata(pattern_noresults, TM_soup)


    if noresultscheck is True:
        print('Check TM entry. You can access: ' + TMURL + '\n'
                                                           'Apparently there are no results for this number. \n Exiting...')
        exit()

    TMrefURL = "https://www.trismegistos.org/ref"
    attestation_URL = TMrefURL + "/ref_list.php?tex_id=" + TMid
    attestation_HTML = urlopen(attestation_URL).read()

    # parses the html. Here you can actually see the Greek characters already

    attestation_SOUP = BeautifulSoup(attestation_HTML, features="html.parser")

    # Gets a list that contains the attested names and the pnrs

    attestations_all = attestation_SOUP.find_all("td", attrs={"class": "cell_2"})[2::4]
    lines_all = attestation_SOUP.find_all("td", attrs={"class": "cell_2"})[1::4]
    attestationsid_all = attestation_SOUP.find_all("td", attrs={"class": "cell_2"})[0::4]

    # converts the html into str so that I can search with regular expressions

    attestations_str = ''.join(map(str, attestations_all))
    lines_str = ''.join(map(str, lines_all))
    attestationsid_str = ''.join(map(str, attestationsid_all))

    pattern_name = re.compile(r'(record=\d+">)(\w+|\.+)')
    pattern_id = re.compile(r"(pnr:\s)(\d+)")
    pattern_line = re.compile(r"(>)(\w+\s?\d+\s?-?\s?\d+?)(</)")  # this one is not used in the end
    pattern_attestationid = re.compile(r"(ref_id=)(\d+)")

    # pattern_action =
    matches_names = pattern_name.finditer(attestations_str)
    matches_ids = pattern_id.finditer(attestations_str)
    matches_lines = pattern_line.finditer(lines_str)
    matches_attestationid = pattern_attestationid.finditer(attestationsid_str)

    # NAMES
    names_list = []
    for match in matches_names:
        names_list.append(match.group(2))
    print(names_list)

    # IDS
    ids_list = []
    for match in matches_ids:
        ids_list.append(match.group(2))
    print(ids_list)

    # LINES
    lines_list = []
    for i in range(len(lines_all)):
        lines_list.append(lines_all[i].text)

    # for match in matches_lines:
    #     lines_list.append(match.group(2))
    print(lines_list)

    # makes a list of attestation ids so that later we can create the URLS to get the action per attestation
    attestation_ids = []
    for match in matches_attestationid:
        attestation_ids.append(match.group(2))
    print(attestation_ids)

    # builds url that leads to single attestation entry, which provides the action
    action_URLs = []
    for i in range(len(attestation_ids)):
        action_URL = TMrefURL + "/detail.php?ref_id=" + attestation_ids[i]
        action_URLs.append(action_URL)

    actions_list = []
    for i in range(len(action_URLs)):
        action_HTML = urlopen(action_URLs[i]).read()
        action_SOUP = BeautifulSoup(action_HTML, features="html.parser")
        action_instance = action_SOUP.find_all("td", attrs={"class": "cell_2"})[3].text
        actions_list.append(action_instance)

    print(actions_list)

    # check len
    if len(names_list) == len(ids_list) == len(attestation_ids) == len(lines_list) == len(actions_list):
        print(colored("lenght ok", "green"))

        # #Importing New Athena Unicode
        pdfmetrics.registerFont(TTFont('New Athena Unicode', "newathu5_7.ttf"))

        # Saving TM attestation data as .txt file

        title_txt = TMid + '_attestations.txt'
        with open(title_txt, 'w', encoding="utf-8") as textfile:  # creates the file
            for i in range(len(names_list)):
                textfile.write(
                    names_list[i] + "(TM Per: " + ids_list[i] + "). " + "Attestation #: " + attestation_ids[i]
                    + ", " + lines_list[i] + ". Action: " + actions_list[i] + "." + "\n")  # writes the content to the file

        # Saving it as .pdf

        document = []
    # CHG2 - changed font family to fontName
        def addTitle(doc):
            doc.append(Spacer(1, 20))
            doc.append(Paragraph(TMid, ParagraphStyle(name="Name", fontName='New Athena Unicode',
                                                      fontsize=18,
                                                      alignment=TA_JUSTIFY)))
            doc.append(Spacer(1, 50))
            return doc


        # CHG-2 added a font to the paragraph, and used font name instead of font family
        currentStyle = ParagraphStyle(name="Name", fontName='New Athena Unicode', fontsize=12, alignment=TA_JUSTIFY)


        def addParagraphs(doc):
            with open(title_txt, 'r', encoding="utf-8", errors="surrogateescape") as txt:
                for line in txt.read().split('\n'):
                    doc.append(Paragraph(line, currentStyle))
                    doc.append(Spacer(1, 12))
            return doc


        document = addTitle(document)

        SimpleDocTemplate(TMid + '(attestations)' + '.pdf', pagesize=letter,
                          rightMargin=12, leftMargin=12,
                          topMargin=12, bottomMargin=6).build(addParagraphs(document))

        os.remove(title_txt)

        again = str(input("Run again? Type y or n: "))
        if again == "n":
            run = False

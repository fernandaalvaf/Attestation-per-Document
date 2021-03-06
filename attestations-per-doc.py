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

# Patterns of the different publication types.
# This will be used to determine how to build the proper URL later.
# Like this, I will be able to make my programs functional for any papyrus, not only from the Zenon archive.

pattern_substring_TM = re.compile(r"\s?[tT][mM]\s?")

#Functions that will be used throughout the code:
    # Function to get the right table within the DDbDP html:

def get_table(soup, table):
    table_soup = soup.find('div', attrs={'class': table})
    return table_soup


    # Function to check for the row containing the data:


def checktargetdata(pattern, text):
    match = re.search(pattern, str(text))
    return bool(match)




run = True

while run:

    print("Hi, this program allows you to save the digitized texts and attestation lists of papyri which are available \n"
          "in the databases papyri.info and Trismegistos.")

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

    elif noresultscheck is False:
        Ref = TM_soup.find_all('a', attrs={'class': 'division-tooltip'})
        DDbDP_pattern = re.compile(r'DDbDP')

    DDbDP_URL = 'Null'

    for element in Ref:
        row_DDbDP_match = DDbDP_pattern.search(str(element))
        if row_DDbDP_match is not None:
            DDbDP_URL = element['href']
            print(DDbDP_URL)

    if DDbDP_URL == 'Null':
        print('No entry in the Duke Databank for Documentary Papyri for this text. \n Exiting...')
        exit()


    # DDbDP HTML

    DDbDP_HTML = urlopen(DDbDP_URL).read()
    DDbDP_r = requests.get(DDbDP_URL)
    DDbDP_soup = BeautifulSoup(DDbDP_r.text, features="html.parser")

    # Getting the metadata of the document. Primarily from oxford-ipap.apis, but if that's not available, from HGV.
    # Table names:
    HGV = 'hgv data'
    TM = 'tm data'
    Oxford = 'apis data'

    # HGV table content:

    HGV_table = get_table(DDbDP_soup, HGV)
    HGV_rows = HGV_table.find_all('tr')

    # Getting the publications from the HGV table:
    pattern_publications = re.compile(r'[P|p]ublications')

    for element in HGV_rows:
        pubcheck = checktargetdata(pattern_publications, element)
        #print(pubcheck)
        if pubcheck is True:
            publication_cell = element.find('td')
            #print(publication_cell)
            publication_moreinfo = publication_cell.find('div')
            publication1 = publication_cell.contents[0].replace(str(publication_moreinfo), '')
            #print(publication1)
            publication2 = publication1.replace("\n", ' ')
            publication = re.sub(' +', ' ',publication2)


    # Getting the title from the HGV table:
    pattern_title = re.compile(r'>[T|t]itle')

    for element in HGV_rows:
        titlecheck = checktargetdata(pattern_title, element)
        if titlecheck is True:
            title_cell = element.find('td')
            title = title_cell.contents[0].replace("['", '').replace("']", '')

    # TM table content:

    TM_table = get_table(DDbDP_soup, TM)
    TM_rows = TM_table.find_all('tr')

    # Getting the date from the TM table:
    pattern_date = re.compile(r'[D|d]ate')

    for element in TM_rows:
        datecheck = checktargetdata(pattern_date, element)
        if datecheck is True:
            date_cell = element.find('td')
            date = date_cell.contents[0].replace("['", '').replace("']", '')

    # Getting Oxford-ipap table content and summary:
    pattern_summary = re.compile(r'[S|s]ummary')
    pattern_multiplespace = re.compile(r'%+')

    Oxford_table = get_table(DDbDP_soup, Oxford)
    if Oxford_table is not None:
        Oxford_rows = Oxford_table.find_all('tr')
        for element in Oxford_rows:
            summarycheck = checktargetdata(pattern_summary, element)
            if summarycheck is True:
                summary_cell = element.find('td')
                summary1 = summary_cell.contents[0].replace("\n", ' ')
                summary = re.sub(' +',' ', summary1)
    else:
        Oxford_rows = None
        summary = 'Not available'

    print('TMid: ', TMid,'\n','title:', title,'\n','pub:', publication,'\n', 'date:',date,'\n','summary:', summary)

    # Getting the Greek text

    greek_text = DDbDP_soup.find_all('div', attrs={'id': 'edition'})[0]


    # Function to keep the line breaks found in the original HTML
    def text_with_newlines(elem):
        text = ''
        for e in elem.descendants:
            if isinstance(e, str):
                text += e.strip()
            elif e.name == 'br' or e.name == 'p':
                text += '\n'
        return text


    final_text = text_with_newlines(greek_text)

    pattern_alias = re.compile(r'(\s)(alias)(\s)')

    TMrefURL = "https://www.trismegistos.org/ref"
    attestation_URL = TMrefURL + "/ref_list.php?tex_id=" + TMid
    attestation_HTML = urlopen(attestation_URL).read()

    # parses the html. Here you can actually see the Greek characters already

    attestation_SOUP = BeautifulSoup(attestation_HTML, features="html.parser")

    # Gets a list that contains the attested names and the pnrs
    attestations_table = attestation_SOUP.find('table', attrs={'class':'info_table'})
    attestations_rows = attestations_table.find_all('tr')
    attestations_all = attestation_SOUP.find_all("td", attrs={"class": "cell_2"})[2::4]


    pattern_alias = re.compile(r'(\s)(alias)(\s)')

    lines_all = attestation_SOUP.find_all("td", attrs={"class": "cell_2"})[1::4]
    attestationsid_all = attestation_SOUP.find_all("td", attrs={"class": "cell_2"})[0::4]

    # converts the html into str so that I can search with regular expressions

    attestations_str = ''.join(map(str, attestations_all))
    lines_str = ''.join(map(str, lines_all))
    attestationsid_str = ''.join(map(str, attestationsid_all))

    #pattern_name = re.compile(r'(record=\d+">)(\w+|\.+)')
    pattern_id = re.compile(r"(pnr:\s)(\d+)")
    pattern_line = re.compile(r"(>)(\w+\s?\d+\s?-?\s?\d+?)(</)")  # this one is not used in the end
    pattern_attestationid = re.compile(r"(ref_id=)(\d+)")


    # pattern_action

    #    matches_names = pattern_name.finditer(attestations_str)
    matches_ids = pattern_id.finditer(attestations_str)
    matches_lines = pattern_line.finditer(lines_str)
    matches_attestationid = pattern_attestationid.finditer(attestationsid_str)

    # NAMES
    names_list = []

    for element in attestations_rows:
        aliascheck = checktargetdata(pattern_alias, element)
        if aliascheck is True:
            temp = element.find_all("td", attrs={"class": "cell_2"})[2::4]
            for i in temp:
                temp1 = temp[0].find_all('a', attrs={'href': True})
                name1 = str(temp1[0].contents).replace("['", '').replace("']", '')
                alias = ' alias '
                name2 = str(temp1[1].contents).replace("['", '').replace("']", '')
                name = str(name1) + alias + str(name2)
                names_list.append(name)
        elif aliascheck is False:
            temp3 = element.find_all("td", attrs={"class": "cell_2"})[2::4]
            for i in temp3:
                temp4 = i.find('a', attrs={'href': True})
                name = str(temp4.contents).replace("['", '').replace("']", '')
                names_list.append(name)
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


    # Saving temporary .txt files:

    # Saving DDbDP data as .txt file

    content = 'Title: '+ title + '\n' +'TMid: ' + TMid + '\n' +'Main publication: '+ publication + '\n' + 'Date: ' + date + '\n' \
              + 'Summary: '+ summary + '\n' + 'Text: '+'\n' + final_text

    title_txt = TMid + '.txt'
    with open(title_txt, 'w', encoding="utf-8") as textfile:  # creates the file
        textfile.write(content)  # writes the content to the file

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
        with open(TMid + ".txt", 'r', encoding="utf-8", errors="surrogateescape") as txt:
            for line in txt.read().split('\n'):
                doc.append(Paragraph(line, currentStyle))
                doc.append(Spacer(1, 12))
        return doc


    document = addTitle(document)

    SimpleDocTemplate(TMid + '(' + publication + ')' + '.pdf', pagesize=letter,
                      rightMargin=12, leftMargin=12,
                      topMargin=12, bottomMargin=6).build(addParagraphs(document))

    os.remove(TMid + ".txt")
    os.remove(title_txt)

    print("papyri to pdf: ok")

    print("both codes: ok")

    again = str(input("Run again? Type y or n: "))
    if again == "n":
        run = False

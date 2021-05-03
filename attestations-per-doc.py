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


run = True # added

while run:

    print("Hi, this program allows you to save the digitized texts and attestation lists of papyri which are available \n"
          "in the databases papyri.info and Trismegistos. So far only the texts belonging to the P.Cairo Zen. are supported.")
    Pub = input("Input the TM id of the text:")


    # Patterns of the different publication types.
    # This will be used to determine how to build the proper URL later.
    # Like this, I will be able to make my programs functional for any papyrus, not only from the Zenon archive.

    # TM ids
    pattern_substring_TM = re.compile(r"\s?[tT][mM]\s?")
    matches_TM = pattern_substring_TM.finditer(Pub)
    pattern_substring_TM2 = re.compile(r"^[^(59)]\d+")

    # P. Cairo Zen. Publications
    pattern_substring_Cairo = re.compile(r"[pP]\.?\s?[Cc][Aa][Ii]\.?\s?[Rr]?\.?\s?[Oo]?\.?\s?[Zz][Ee][Nn]\.?")
    matches_Cairo = pattern_substring_Cairo.finditer(Pub)

    # P.Lond.
    pattern_substring_Lond = re.compile(r"[Pp]\.?\s?[Ll][Oo][Nn][Dd]\.?\s?")
    matches_Lond = pattern_substring_Lond.finditer(Pub)


    # Function to identify what type of publication was input by the user.
    def pub_check(txt):
        if bool(re.search(pattern_substring_TM, txt)) == True:
            print("TM publication")
        elif bool(re.search(pattern_substring_Cairo, txt)) == True:
            print("P.Cairo Zen. publication")
        elif bool(re.search(pattern_substring_Lond, txt)) == True:
            print("P.Lond. publication")


    pub_check(Pub)

    # Now we need to build the URL

    Papyri_info_baseURL = "https://papyri.info/ddbdp/"
    TM_baseURL = "https://www.trismegistos.org/text/"

    # TM id:

    TMid_pattern = re.compile(r"(\s?[tT][mM]\s?)(\d+)")
    TMid_match = TMid_pattern.finditer(Pub)


    for match in TMid_match:
        TMid = match.group(2)


    print(TMid)

    TMURL = TM_baseURL + TMid
    TM_HTML = urlopen(TMURL).read()
    TM_r = requests.get(TMURL)
    TM_soup = BeautifulSoup(TM_r.text, features="html.parser")
    Ref = TM_soup.find_all('a', attrs={'class': 'division-tooltip'})

    link = str(Ref)

    #alterations start here

    pattern_papyriinfo = re.compile(r'(papyri\.info)(.*)(target="_blank">DDbDP)')
    match_papyriinfo = pattern_papyriinfo.search(link)
    papyriinfo_link = str(match_papyriinfo[2]).replace('"','')

    print(papyriinfo_link)

    pattern_link = re.compile(r"(P\.Cair\.zen;)(\d)(;)(\d+)")
    match_link = pattern_link.finditer(link)

    publs = TM_soup.find_all('div', attrs={'id': 'text-publs'})[0].get_text()

    pcz_pattern = re.compile(r'(zen;)(\d)(;)(\d+)')
    pcz_match = pcz_pattern.match(papyriinfo_link)
    pcz = pcz_pattern.findall(papyriinfo_link)

    pcz_pub_pattern = re.compile(r'(Caire)(\s)(\d)(\s)(\d+)')
    pcz_pub = pcz_pub_pattern.findall(publs)


    if pcz_match is not None:
        VolumeIndex = pcz[0][1]
        Document_id = pcz[0][3]
    else:
        VolumeIndex = pcz_pub[0][2]
        Document_id = pcz_pub[0][4]



    PapyriInfoUrl = "http://papyri.info" + papyriinfo_link
    print(PapyriInfoUrl)



    # #and the ids that are taken from it...
    PapyriInfoIds = range(59001, 59854)


    # cheatsheet to the volumes and numbers of the corpus
    print("Vol 1 (p.cair.zen;1;59xxx series): from 59001 to 59139.\n"
          "Vol 2 (p.cair.zen;2;59xxx series): from 59140 to 59297.\n"
          "Vol 3 (p.cair.zen;3;59xxx series): from 59298 to 59531.\n"
          "Vol 4 (p.cair.zen;4;59xxx series): from 59532 to 59800.\n"
          "Vol 5 (p.cair.zen;5;59xxx series): from 59801 to 59853.")

    completeUrl = PapyriInfoUrl #+ VolumeIndex + ';' + Document_id  # For each element we create the URL to query
    print(completeUrl)

    html = urlopen(completeUrl).read()
    soup = BeautifulSoup(html, features="html.parser")



    # Getting the metadata of the document
    title = soup.find_all('td', attrs={'class': 'mdtitle'})[0].text
    summary = soup.find_all('table', attrs={'class': 'metadata'})[2].find_all('td')[1].text
    date = soup.find_all('table', attrs={'class': 'metadata'})[1].find_all('td')[2].text
    tm_id = soup.find('div', attrs={'class': 'tm data'}).find('h2').text.replace("[source]","")
    pcairz_id = soup.find_all('table', attrs={'class': 'metadata'})[2].find_all('td')[2].text

    print(tm_id)
    # Getting the Greek text

    greek_text = soup.find_all('div', attrs={'id': 'edition'})[0]


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

    # Saving it as .txt file

    content = title + '\n' + tm_id + '\n' + pcairz_id + '\n' + date + '\n' + summary + '\n' + final_text

    title_txt = Document_id + '.txt'
    with open(title_txt, 'w', encoding="utf-8") as textfile:  # creates the file
        textfile.write(content)  # writes the content to the file

    # #Importing New Athena Unicode
    pdfmetrics.registerFont(TTFont('New Athena Unicode', "newathu5_7.ttf"))

    # Building the URL for the attestation list page

    # TMid = input("TM id:")

    core_URL = "https://www.trismegistos.org/ref"
    attestation_URL = core_URL + "/ref_list.php?tex_id=" + TMid

    # Gets the html code for the given url. All the unicode characters are shown by their code at this stage

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
        action_URL = core_URL + "/detail.php?ref_id=" + attestation_ids[i]
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

    # Saving it in a document
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
        with open(Document_id + ".txt", 'r', encoding="utf-8", errors="surrogateescape") as txt:
            for line in txt.read().split('\n'):
                doc.append(Paragraph(line, currentStyle))
                doc.append(Spacer(1, 12))
        return doc


    document = addTitle(document)

    SimpleDocTemplate(TMid +'(' + Document_id + ')'+ '.pdf', pagesize=letter,
                      rightMargin=12, leftMargin=12,
                      topMargin=12, bottomMargin=6).build(addParagraphs(document))

    os.remove(Document_id + ".txt")
    os.remove(title_txt)

    print("papyri to pdf: ok")

    print("both codes: ok")

    again=str(input("Run again? Type y or n: "))
    if again == "n":
        run = False

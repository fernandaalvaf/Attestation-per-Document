import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import unicodedata
import re
from termcolor import colored
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from codecs import StreamRecoder
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def checktargetdata(pattern, text):
    match = re.search(pattern, str(text))
    return bool(match)


# Building the URL for the attestation list page

TMid = input("TM id:")

core_URL = "https://www.trismegistos.org/ref"
attestation_URL = core_URL + "/ref_list.php?tex_id=" + TMid

# Gets the html code for the given url. All the unicode characters are shown by their code at this stage

attestation_HTML = urlopen(attestation_URL).read()

# parses the html. Here you can actually see the Greek characters already

attestation_SOUP = BeautifulSoup(attestation_HTML, features="html.parser")

# Gets a list that contains the attested names and the pnrs

attestations_all = attestation_SOUP.find_all("td", attrs={"class":"cell_2"})[2::4]
lines_all = attestation_SOUP.find_all("td", attrs={"class":"cell_2"})[1::4]
attestationsid_all = attestation_SOUP.find_all("td", attrs={"class":"cell_2"})[0::4]
attestations_table = attestation_SOUP.find('table', attrs={'class':'info_table'})
attestations_rows = attestations_table.find_all('tr')
# converts the html into str so that I can search with regular expressions

attestations_str = ''.join(map(str, attestations_all))
lines_str = ''.join(map(str, lines_all))
attestationsid_str = ''.join(map(str, attestationsid_all))

#Theoretically, I was supposed to be able to get the data from the text, store it and loop until done.
pattern_name = re.compile(r'(record=\d+">)(\w+|\.+)')
pattern_id = re.compile(r"(pnr:\s)(\d+)")
pattern_line = re.compile(r"(>)(\w+\s?\d+\s?-?\s?\d+?)(</)") # this one is not used in the end
pattern_attestationid = re.compile(r"(ref_id=)(\d+)")

# pattern_action =
matches_names = pattern_name.finditer(attestations_str)
matches_ids = pattern_id.finditer(attestations_str)
matches_lines = pattern_line.finditer(lines_str)
matches_attestationid = pattern_attestationid.finditer(attestationsid_str)

#NAMES
names_list = []
pattern_alias = re.compile(r'(\s)(alias)(\s)')

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

#IDS
ids_list = []
for match in matches_ids:
    ids_list.append(match.group(2))
print(ids_list)

#LINES
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
    action_instance = action_SOUP.find_all("td", attrs={"class":"cell_2"})[3].text
    actions_list.append(action_instance)

print(actions_list)

#check len
if len(names_list) == len(ids_list) == len(attestation_ids) == len(lines_list) == len(actions_list):
    print(colored("lenght ok", "green"))

#Saving it in a document
title_txt = TMid + '_attestations.txt'
with open(title_txt, 'w', encoding="utf-8") as textfile:  #creates the file
    for i in range(len(names_list)):
        textfile.write(
            names_list[i] + "(TM Per: " + ids_list[i] + "). " + "Attestation #: " + attestation_ids[i]
            + ", " + lines_list[i] + ". Action: " + actions_list[i] + "." + "\n") #writes the content to the file

#Saving it as .pdf

document = []


#CHG2 - changed font family to fontName
def addTitle(doc):
    doc.append(Spacer(1, 20))
    doc.append(Paragraph(TMid, ParagraphStyle(name="Name",fontName='Helvetica',
                                                 fontsize=18,
                                                 alignment=TA_JUSTIFY)))
    doc.append(Spacer(1,50))
    return doc

#CHG-2 added a font to the paragraph, and used font name instead of font family
currentStyle = ParagraphStyle(name="Name",fontName='Helvetica', fontsize=12, alignment=TA_JUSTIFY)

def addParagraphs(doc):
    with open(title_txt, 'r',  encoding="utf-8", errors="surrogateescape") as txt:
        for line in txt.read().split('\n'):
            doc.append(Paragraph(line, currentStyle))
            doc.append(Spacer(1,12))
    return doc

document = addTitle(document)

SimpleDocTemplate(TMid + '_attestations.pdf', pagesize=letter,
                  rightMargin=12, leftMargin=12,
                  topMargin=12, bottomMargin=6).build(addParagraphs(document))

os.remove(TMid + "_attestations.txt")

print("ok")

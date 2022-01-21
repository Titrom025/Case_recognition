# %%
import re
import random   
import io
import time
import os
import json
from shutil import move

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams

from pdf2image import convert_from_path
from PIL import ImageDraw, ImageFont

from navec import Navec
from slovnet import NER

import extractors
from utils import createDirIfNotExist, createDir, get_files
from words_handler import parse_obj, highlightObjects, DPI_SCALE, STANDART_DPI
from object_handlers import handleNumbers, handlePersons, handleDates, handleMoney, handleOrgs, handlePassport

# %%
records = {}
def addToXML(obj, bbox, page_num):
  obj_postfix = records.get(obj['field_type'], 1)
  records[obj['field_type']] = obj_postfix + 1
  res_string = ''
  if XML_FORMAT == 'NamedResult':
    res_string = \
"""      <NamedResult>
        <Title>{title}</Title>
        <Result xsi:type="TextResult">
          <Area>
            <Location>
              <X>{x}</X>
              <Y>{y}</Y>
            </Location>
            <Size>
              <Width>{w}</Width>
              <Height>{h}</Height>
            </Size>
            <X>{x}</X>
            <Y>{y}</Y>
            <Width>{w}</Width>
            <Height>{h}</Height>
          </Area>
          <IsFound>true</IsFound>
          <PageNumber>{page_num}</PageNumber>
          <Text>{text}</Text>
          <Confidence>99</Confidence>
        </Result>
      </NamedResult>
""".format(title=obj['field_type'] + '_' + str(obj_postfix), x=bbox[0], y=bbox[1], 
                               w=bbox[0]-bbox[2], h=bbox[1]-bbox[3], 
                               page_num=page_num, text=obj['text_value'])
  else:                
    res_string = '  <{field_type} value="{value}" confidence="100" page="{page}" left="{x}" top="{y}" width="{w}" height="{h}"/>' \
            .format(field_type=obj['field_type'] + '_' + str(obj_postfix),
                value=obj["text_value"].replace('"', '').replace('<', '').replace('>', ''),
                x=bbox[2], y=bbox[1], w=bbox[2]-bbox[0], h=bbox[1]-bbox[3], page=pageNum) + '\n'

  xml.write(res_string)

                               
def saveToXML(objects, docName, images, xml, maxPageNum, processedText, text_lines, drawnBoxes, xmlsBoxes, border_colors):  
  font = ImageFont.truetype("Arsenal-Regular.otf", 20)

  unique_values = set()
  objects = [o for o in objects
      if (o['text_value'], o['bbox']) not in unique_values
      and not unique_values.add((o['text_value'], o['bbox']))]

  nums_objs = handleNumbers(objects, images[0].size[1])
  persons_objs = handlePersons(objects, images[0].size[1], processedText, text_lines, drawnBoxes, xmlsBoxes, 0, border_colors)
  dates_objs = handleDates(objects, images[0].size[1])
  money_objs = handleMoney(objects, images[0].size[1])
  orgs_objs = handleOrgs(objects, images[0].size[1], images[0].size[0])
  passport_objs = handlePassport(objects, images[0].size[0])
  objects = persons_objs + dates_objs + nums_objs + money_objs + orgs_objs + passport_objs
  
  for page_num in range(0, maxPageNum):
    im_height = images[page_num].size[1]
    image_drawer = ImageDraw.Draw(images[page_num])
    
    for obj in objects:
      if obj["pageNum"] != page_num:
        continue
      
      bbox = (obj["bbox"][0], int(im_height - obj["bbox"][1] - page_num * 10000),
          obj["bbox"][2], int(im_height - obj["bbox"][3] - page_num * 10000))

      image_drawer.rectangle((bbox[0], bbox[1], bbox[2], bbox[3] + random.randint(2, 10)), 
                  outline=border_colors[obj['field_type']], width=3)
      
      image_drawer.rectangle((bbox[0], bbox[3], bbox[2], bbox[3]-20), fill="white")

      image_drawer.text((bbox[0], bbox[3]-20), obj['field_type'] + " | " + obj["text_value"], 
                font = font, fill=border_colors[obj['field_type']])

      addToXML(obj, bbox, page_num)
      
    images[page_num].save("results/" + docName + "_" + str(page_num) + ".jpg", "JPEG")
    

# %%
if __name__ == '__main__':
  CONFIG_PATH = "config.json"
  with open(CONFIG_PATH) as f:
    config = json.load(f)

  XML_FORMAT = config['XML_FORMAT']
  # XML_FORMAT = 'NamedResult'
  # XML_FORMAT = 'idcard'

  MODEL_NAME = 'model'
  PDF_PATH = "input/"
  HANDLED_PATH = "handled/"
  SLEEP_TIME = 5

  border_colors = {
    'Number': 'red',
    'Date': 'deepskyblue',
    'Org': 'blue',
    'Money': 'green',
    'Debtor': 'orange',
    'Person': 'black',
    'Judge': 'yellow',
    'DebtorDate': 'purple',
    'LetterNumber': 'pink',
    'LetterDate': 'gray', 
    'PassportNum': 'red',
    'PassportSeries': 'red'
  }

  la_params = LAParams()
  la_params.line_margin = 1.6
  la_params.boxes_flow = 0.5

  createDirIfNotExist(PDF_PATH)
  createDirIfNotExist(HANDLED_PATH)
  createDir("results/", ".jpg")
  createDir("xmls/", ".xml")

  navec = Navec.load('vocab.tar')
  ner = NER.load(MODEL_NAME + '.tar')
  ner.navec(navec)

  while True:
    for doc_name in get_files(PDF_PATH, ".pdf"):
      images = convert_from_path(PDF_PATH + doc_name, dpi = STANDART_DPI * DPI_SCALE)

      fp = open(PDF_PATH + doc_name, 'rb')
      parser = PDFParser(fp)
      document = PDFDocument(parser)
      
      xml = io.open("xmls/" + doc_name.replace('.pdf', '') + ".xml", "w", encoding="utf-8")

      if XML_FORMAT == 'NamedResult':
        xml.write(
"""<?xml version="1.0" encoding="utf-8"?>
<ArrayOfResultModel xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <ResultModel>
    <DocClass>Russian Marriage Certificate</DocClass>
    <PagesOnOriginalImage>
      <int>{pages_count}</int>
    </PagesOnOriginalImage>
    <NumberOfPages>1</NumberOfPages>
    <Data>
""".format(pages_count = len(images)))
      else:
        xml.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
        xml.write('<idcard>' + '\n')

      drawnBoxes = []
      xmlsBoxes = []
      maxPageNum = 0
      
      for pageNum, page in enumerate(PDFPage.create_pages(document)):
        actName = doc_name.split(".")[0] + "_" + str(pageNum) 
        print(actName)

        text_lines = []
        
        rsr_mgr = PDFResourceManager()
        device = PDFPageAggregator(rsr_mgr, laparams=la_params)
        
        interpreter = PDFPageInterpreter(rsr_mgr, device)
        interpreter.process_page(page)
        
        layout = device.get_result()
        rawText = parse_obj(layout._objs, text_lines)

        processedText = re.sub(r"__+", r" ", rawText)

        if len(processedText) == 0:
          break

        markup = ner(processedText)
            
        extracted_nums = extractors.extractNums(processedText)
        highlightObjects(extracted_nums, 'Number', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        extracted_dates = extractors.extractDates(processedText)
        highlightObjects(extracted_dates, 'Date', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        extracted_orgs, extracted_persons = extractors.extractOrgs(markup)
        highlightObjects(extracted_orgs, 'Org', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        extracted_persons = extractors.extractPersons(processedText, markup)
        highlightObjects(extracted_persons, 'Person', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        extracted_debtors = extractors.extractDebtors(processedText)
        highlightObjects(extracted_debtors, 'Debtor', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        extracted_money = extractors.extractMoney(processedText)
        highlightObjects(extracted_money, 'Money', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        extracted_passport_series = extractors.extractPassportSeries(processedText)
        highlightObjects(extracted_passport_series, 'PassportSeries', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        extracted_passport_nums = extractors.extractPassportNums(processedText)
        highlightObjects(extracted_passport_nums, 'PassportNum', text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)

        maxPageNum += 1
        
      saveToXML(xmlsBoxes, doc_name.replace('.pdf', ''), images, xml, maxPageNum, processedText, text_lines, drawnBoxes, xmlsBoxes, border_colors)

      if XML_FORMAT == 'NamedResult':
        xml.write(
"""    </Data>
  </ResultModel>
</ArrayOfResultModel>""")
      else:
        xml.write('</idcard>' + '\n')

      xml.close()

      fp.close()
      move(PDF_PATH + doc_name, HANDLED_PATH + doc_name)

    time.sleep(SLEEP_TIME)



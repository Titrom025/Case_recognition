import re

from natasha import (
    MorphVocab,
    AddrExtractor,
)

morph_vocab = MorphVocab()
addr_extractor = AddrExtractor(morph_vocab)

def extractNums(processedText):    
  actNumbers = re.findall(r"№ ?[^ /,\n][^ ,\n]+", processedText)
  actNumbers = list(filter(lambda number: len(re.sub(r"[№ от]", r"", number)) > 3, actNumbers))
  return [[num] for num in actNumbers]

def extractPassportSeries(processedText):    
  passport_series = re.findall(r"[№ ]\d{4} ", processedText)
  return [[series] for series in passport_series]

def extractPassportNums(processedText):    
  passport_nums = re.findall(r"[№ ]\d{6}[ ,.]", processedText)
  return [[series] for series in passport_nums]
        
        
def extractDates(processedText):    
  datesArr = re.findall(r" «? ?\d{1,2} ?»?[^0-9/]{1,2}(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|(?:0[1-9]|1[0-2]))[^0-9/]{1,2}(?:(?:19|20)\d{2}|[89012]\d)", processedText)
  return [[date.strip()] for date in datesArr]

ORGS_BLACK_LIST = ['ирово', 'уфмс', 'суд', 'бик', 'район', 'банк', 'именем', 'дело', 'северо'] 
def extractOrgs(markup):  
  orgsArr = []
  personsArr = []
  for span in markup.spans:
    if span.type == "ORG" and span.stop - span.start > 10:
      org = markup.text[span.start:span.stop]
      org = re.sub(r"  +", r" ", org)
      org = org.strip()
      if (len(org.split(' ')) == 1):
        personsArr.append(org.split(' '))
      else:
        org_s = org.lower()
        correct_org = True
        for word in ORGS_BLACK_LIST:
          if word in org_s:
            correct_org = False
            break

        if correct_org:
          orgsArr.append(org.split(' '))

  return orgsArr, personsArr


def extractMoney(processedText):
  # moneyArr = re.findall(r"\d{1,3}[ \-\']?\d{1,3}[ \-\']?\d{1,3}[,.]\d{2}? *(?:[Рр][Уу][Бб])?", processedText)
  moneyArr = re.findall(r"\d{0,3}[ \']*\d{0,3}[ \']*\d{1,3}[,.]?\d{0,2} *(?:[Рр][Уу][Бб])", processedText)
  return [re.split(r' *[Рр][Уу][Бб]', money)[:-1] + re.findall(r'[Рр][Уу][Бб]', money) for money in moneyArr]

      
def extractPersons(processedText, markup):    
  personsArr = []
  markup_persons = []

  persons = re.findall(r"(?:[A-Я][А-я]{4,} [A-Я][\.,] ?[A-Я][\.,])|(?:[A-Я][\.,] ?[A-Я][\.,] ?[A-Я][А-я]{4,})", processedText)

  for span in markup.spans:
    if span.type == "PER" and span.stop - span.start > 5:
      per = markup.text[span.start:span.stop]
      per = per.strip()
      per = re.sub(r"  +", r" ", per)
      markup_persons.append(per)

  has_changes = True
  while has_changes:
    has_changes = False
    for person in persons:
      for per in markup_persons:
        if person in per or per in persons:
          markup_persons.remove(per)
          has_changes = True
          break
              
  for person in markup_persons:     
    person = person.strip()
    person = re.sub(r"  +", r" ", person)
    if len(re.sub(r"[ .]", r"", person)) > 4:
      personsArr.append(person.split(" "))
  
  for person in persons:     
    person = person.strip()
    person = re.sub(r"  +", r" ", person)
    if len(re.sub(r"[ .]", r"", person)) > 4:
      personsArr.append(person.split(" "))

  return personsArr


def extractDebtors(processedText):
  debtors = re.findall(r"должник[^А-Я]{1,5}([А-Я][^А-Я]{1,20}[А-Я][^А-Я]{1,15}[А-Я][^., ;]{1,15})", processedText)
  return [debtor.split(' ') for debtor in debtors]


def extractAddresses(text_lines):   
    adresses = [] 
    print("\nAddresses:")
    for i in range(len(text_lines) - 1):
        textBox = text_lines[i]
        text = textBox.get_text()
        address1 = addr_extractor.find(text)
        if address1 is not None:
            address1words = []
            parts = address1.fact.parts

            for part in parts:
                if part.value is not None:
                    address1words.append(part.value)

            if len(address1words) == 0:
                continue

            if len(address1words) == 1 and parts[0].type != "город":
                continue

            textBoxNext = text_lines[i+1]
            textNext = textBoxNext.get_text()
            address2 = addr_extractor.find(text + " " + textNext)
            if address2 is not None:
                address2words = []
                parts = address2.fact.parts

                for part in parts:
                    if part.value is not None:
                        address2words.append(part.value)

                print("-", ' '.join(address2words))
                adresses.append(address2words)
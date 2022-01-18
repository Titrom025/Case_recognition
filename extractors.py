import re

def extractNums(processedText):    
  actNumbers = re.findall(r"№ ?[^ /,\n][^ ,\n]+", processedText)
  actNumbers = list(filter(lambda number: len(re.sub(r"[№ от]", r"", number)) > 3, actNumbers))
  return [[num] for num in actNumbers]
        
        
def extractDates(processedText):    
  datesArr = re.findall(r" «? ?\d{1,2} ?»?[^0-9/]{1,2}(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|(?:0[1-9]|1[0-2]))[^0-9/]{1,2}(?:(?:19|20)\d{2}|[89012]\d)", processedText)
  return [[date.strip()] for date in datesArr]

                
def extractOrgs(markup):  
  orgsArr = []
  personsArr = []
  for span in markup.spans:
    if span.type == "ORG" and span.stop - span.start > 5:
      org = markup.text[span.start:span.stop]
      org = org.strip()
      if (len(org.split(' ')) == 1):
        personsArr.append(org.split(' '))
      else:
        if not ('ирово' in org or 'УФМС' in org or 'суд' in org or 'БИК' in org):
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

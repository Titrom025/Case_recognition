import re
from utils import checkSimilarity
from words_handler import findAndHighlight

RECEIVER_ORGS = {'коллект':'ООО «АйДи Коллект'}

def handleNumbers(objects, im_height):
	numbers_objs = list(filter(lambda obj: obj['field_type'] == 'Number'
					and obj["bbox"][3] > 0
					and (len(obj["text_value"]) > 6
					and obj["bbox"][3] > im_height * 0.8), objects))
	numbers_objs = sorted(numbers_objs, key = lambda obj: obj['bbox'][3], reverse=True)

	nums = []
	if len(numbers_objs) > 0:
		numbers_objs[0]['field_type'] = 'LetterNumber'
		nums.append(numbers_objs[0])

	return nums

def handleMoney(objects, im_height):
	money_objs = list(filter(lambda obj: obj['field_type'] == 'Money', objects))
	money_objs = sorted(money_objs, key = lambda obj: obj['bbox'][3], reverse=True)

	return money_objs


def handlePassport(objects, im_height):
	passport_series_objs = list(filter(lambda obj: obj['field_type'] == 'PassportSeries', objects))
	passport_series_objs = sorted(passport_series_objs, key = lambda obj: obj['bbox'][3], reverse=True)

	passport_nums_objs = list(filter(lambda obj: obj['field_type'] == 'PassportNum', objects))
	passport_nums_objs = sorted(passport_nums_objs, key = lambda obj: obj['bbox'][3], reverse=True)

	for series_index, series_obj in enumerate(passport_series_objs):
		for num_index, num_obj in enumerate(passport_nums_objs):
			if (series_obj["bbox"][3] < num_obj["bbox"][3] + 10 \
					and (series_obj["bbox"][1] > num_obj["bbox"][1] - 10) \
					and abs(series_obj["bbox"][2] - num_obj["bbox"][0]) < 200) \
				or (abs(series_obj["bbox"][1] - num_obj["bbox"][3]) < 30 \
					and (series_obj["bbox"][1] - num_obj["bbox"][1] < 100) \
					and series_obj["bbox"][0] - num_obj["bbox"][2] > 1500):
				passport_series_objs[series_index]['field_type'] = 'PassportSeries'
				passport_nums_objs[num_index]['field_type'] = 'PassportNum'
				print(passport_series_objs[series_index]['bbox'])
				print(passport_nums_objs[num_index]['bbox'])
				return [passport_series_objs[series_index], passport_nums_objs[num_index]]

	# passport_series_objs = list(filter(lambda obj: (obj['field_type'] == 'PassportSeries'), passport_series_objs))
	# passport_nums_objs = list(filter(lambda obj: (obj['field_type'] == 'PassportNum'), passport_nums_objs))

	# print(passport_series_objs + passport_nums_objs)
	return []

 
def handleDates(objects, im_height):
	dates = []
	dates_objs = list(filter(lambda obj: obj['field_type'] == 'Date'
					and obj["bbox"][3] > 0, objects))
	dates_objs = sorted(dates_objs, key = lambda obj: obj['bbox'][3], reverse=True)

	debtors_objs = list(filter(lambda obj: (obj['field_type'] == 'Debtor'), objects))
	debtors_objs = sorted(debtors_objs, key = lambda obj: obj["bbox"][3], reverse=True)

	for index, date_obj in enumerate(dates_objs):
		for debtor_obj in debtors_objs:
			if (date_obj["bbox"][3] > debtor_obj["bbox"][1] - 20) and (date_obj["bbox"][3] < debtor_obj["bbox"][3] + 40):
				dates_objs[index]['field_type'] = 'DebtorDate'
				break
				
	debtor_dates_objs = list(filter(lambda obj: (obj['field_type'] == 'DebtorDate'), dates_objs))

	if len(debtor_dates_objs) > 0:
		dates.append(debtor_dates_objs[0])

	LetterNumbers_objs = list(filter(lambda obj: obj['field_type'] == 'LetterNumber', objects))
	if len(LetterNumbers_objs) > 0:
		letterNumber_obj = LetterNumbers_objs[0]
		for index, date_obj in enumerate(dates_objs):
			if (date_obj["bbox"][3] > letterNumber_obj["bbox"][1] - 100) and (date_obj["bbox"][3] < letterNumber_obj["bbox"][3] + 40):
				dates_objs[index]['field_type'] = 'LetterDate'
				break
	else:
		if len(dates_objs) > 0:
			if dates_objs[0]['field_type'] == 'Date':
				dates_objs[0]['field_type'] = 'LetterDate'


	letter_dates_objs = list(filter(lambda obj: (obj['field_type'] == 'LetterDate'), dates_objs))

	if len(letter_dates_objs) > 0:
		dates.append(letter_dates_objs[0])

	return dates


def handlePersons(objects, im_height, processedText, text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors):
	top_person_objs = list(filter(lambda obj: (obj['field_type'] == 'Person' 
							and len(re.findall(r"[А-Я]", obj['text_value'])) >= 3
							and (len(obj["text_value"].split(" ")) > 1 or len(obj["text_value"].split(".")) > 1)
							and 'мировой' not in obj['text_value'].lower()
							and obj["bbox"][3] > im_height * 0.6), objects))
	top_person_objs = sorted(top_person_objs, key = lambda obj: obj["bbox"][3], reverse=True)

	top_debtors_objs = list(filter(lambda obj: (obj['field_type'] == 'Debtor'), objects))
	top_debtors_objs = sorted(top_debtors_objs, key = lambda obj: obj["bbox"][3], reverse=True)

	if len(top_person_objs) > 2:
		top_person_objs = top_person_objs[0:2]

	if len(top_debtors_objs) > 1:
		top_debtors_objs = top_debtors_objs[0:1]
  
	if len(top_person_objs) > 0:
		if len(top_debtors_objs) > 0:
			top_person = top_person_objs[0]["text_value"]
			debtor_person = top_debtors_objs[0]["text_value"]
			if not checkSimilarity(top_person, debtor_person):
				top_person_objs[0]['field_type'] = 'Judge'
		else:
			top_person_objs[0]['field_type'] = 'Judge'
			if len(top_person_objs) > 1:
				top_person_objs[1]['field_type'] = 'Debtor'
    
	top_person_objs = list(filter(lambda obj: (obj['field_type'] != 'Person'), top_person_objs))
	top_debtors_objs = list(filter(lambda obj: (obj['field_type'] != 'Person'), top_debtors_objs))

	debtor_name = ''
	if len(top_debtors_objs) > 0:
		debtor_name = top_debtors_objs[0]["text_value"]
	elif len(top_person_objs) > 1:
		debtor_name = top_person_objs[1]["text_value"]

	if debtor_name != '':
		findAndHighlight(debtor_name, 'Debtor', processedText, text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)
		persons_objs = list(filter(lambda obj: (obj['field_type'] == 'Person'), objects))
		for index, person_obj in enumerate(persons_objs):
			person_name = person_obj["text_value"]
			if checkSimilarity(person_name, debtor_name):
				persons_objs[index]['field_type'] = 'Debtor'
				findAndHighlight(person_name, 'Debtor', processedText, text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)
  
	return top_person_objs + top_debtors_objs


def handleOrgs(objects, im_height, im_width):
	top_orgs_objs = list(filter(lambda obj: (obj['field_type'] == "Org" 
								and (len(obj["text_value"].split(" ")) > 1 
								or len(obj["text_value"].split("«")) > 1)
								and obj["bbox"][3] > im_height * 0.4), objects))
	top_orgs_objs = sorted(top_orgs_objs, key = lambda obj: obj["bbox"][3], reverse=True)

	for index, org in enumerate(top_orgs_objs):
		org_s = org['text_value'].lower()
		for dict_org in RECEIVER_ORGS:
			if dict_org in org_s:
				top_orgs_objs[index]['text_value'] = RECEIVER_ORGS[dict_org]
				break

	unique_orgs = []
	unique_values = set()
	for org in top_orgs_objs:
		unique_value = True
		for org_dict in unique_values:
			if checkSimilarity(org_dict, org['text_value']):
				unique_value = False
				break

		if unique_value:
			unique_orgs.append(org)
			unique_values.add(org['text_value'])

	return unique_orgs

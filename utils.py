import re

def checkSimilarity(string1, string2):
	string1_normal = re.sub(r"[ .,]", r"", string1)
	string1_normal = string1_normal.lower()
	string2_normal = re.sub(r"[ .,]", r"", string2)
	string2_normal = string2_normal.lower()

	similarity = True
	for char in string1_normal:
		if char not in string2_normal:
			similarity = False
			break

	for char in string2_normal:
		if char not in string1_normal:
			similarity = False
			break

	return similarity
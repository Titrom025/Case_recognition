import re
import os

def get_files(dirpath, ext):
  files = [s for s in os.listdir(dirpath)
     if os.path.isfile(os.path.join(dirpath, s)) and os.path.splitext(s)[1] == ext]
  files.sort()
  return files


def createDir(dirpath, ext):
  if os.path.exists(dirpath):
    for file in get_files(dirpath, ext):
      os.remove(os.path.join(dirpath, file))
  else:
    os.mkdir(dirpath)
    
def createDirIfNotExist(dirpath):
  if not os.path.exists(dirpath):
    os.mkdir(dirpath)

def checkSimilarity(string1, string2, similarity=0.8):
	string1_normal = re.sub(r"[ .,]", r"", string1)
	string1_normal = string1_normal.lower()
	string2_normal = re.sub(r"[ .,]", r"", string2)
	string2_normal = string2_normal.lower()

	total_chars = len(string1_normal) + len(string2_normal)
	similar_chars = 0
	for char in string1_normal:
		if char in string2_normal:
			similar_chars += 1

	for char in string2_normal:
		if char in string1_normal:
			similar_chars += 1

	return (similar_chars > total_chars * similarity)
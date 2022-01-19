import pdfminer
import re

DPI_SCALE = 4.17
STANDART_DPI = 72

def draw_words(first_line_index, last_line_index, words, text_lines,
        drawn_boxes, xmls_boxes, pageNum, field_type, border_color):
  
  if first_line_index == last_line_index:
    
    first_line = text_lines[first_line_index]
    chars = []
    for elem in first_line._objs:
      if isinstance(elem, pdfminer.layout.LTChar):
        chars.append(elem)    
    first_line._objs = chars
    first_line_text = first_line.get_text()

    x_left = first_line_text.index(words[0])
    offset = x_left
    for word in words[:len(words)-1]:
      offset += len(word)

    if len(words) == 1:
      x_right = x_left + len(words[0]) - 1
    else:
      x_right = first_line_text.find(words[len(words) - 1], offset) + len(words[len(words) - 1]) - 1
    
    if x_right == -1:
      return False
    
    return drawElement(
        first_line._objs[x_left].bbox[0] - 2, 
        first_line._objs[x_left].bbox[1] - 3,
        first_line._objs[x_right].bbox[2] + 2,
        first_line._objs[x_right].bbox[3] + 3,
        ' '.join(words),
        drawn_boxes, xmls_boxes, pageNum,
        field_type=field_type, border_color=border_color
    )
  else:
    
    first_line = text_lines[first_line_index]
    chars = []
    for elem in first_line._objs:
      if isinstance(elem, pdfminer.layout.LTChar):
        chars.append(elem)    
    first_line._objs = chars
    first_line_text = first_line.get_text()

    x_left = first_line_text.index(words[0])

    if drawElement(
        first_line._objs[x_left].bbox[0] - 2, 
        first_line._objs[x_left].bbox[1] - 3,
        first_line._objs[len(first_line._objs) - 1].bbox[2] + 2,
        first_line._objs[len(first_line._objs) - 1].bbox[3] + 3,
        ' '.join(words),
        drawn_boxes, xmls_boxes, pageNum,
        field_type=field_type, border_color=border_color):
      
      last_line = text_lines[last_line_index]
      chars = []
      for elem in last_line._objs:
        if isinstance(elem, pdfminer.layout.LTChar):
          chars.append(elem)    
      last_line._objs = chars
      last_line_text = last_line.get_text()

      x_right = last_line_text.index(words[len(words) - 1]) + len(words[len(words) - 1]) - 1

      drawElement(
          last_line._objs[0].bbox[0] - 2, 
          last_line._objs[0].bbox[1] - 3,
          last_line._objs[x_right].bbox[2] + 2,
          last_line._objs[x_right].bbox[3] + 3,
          ' '.join(words),
          drawn_boxes, xmls_boxes, pageNum,
          field_type=field_type, border_color=border_color)
      
      for middle_line_index in range(first_line_index + 1, last_line_index):
        middle_line = text_lines[middle_line_index]
        chars = []
        for elem in middle_line._objs:
          if isinstance(elem, pdfminer.layout.LTChar):
            chars.append(elem)    
        middle_line._objs = chars

        drawElement(
            middle_line._objs[0].bbox[0] - 2, 
            middle_line._objs[0].bbox[1] - 3,
            middle_line._objs[len(middle_line._objs) - 1].bbox[2] + 2,
            middle_line._objs[len(middle_line._objs) - 1].bbox[3] + 3,
            ' '.join(words),
            drawn_boxes, xmls_boxes, pageNum,
            field_type=field_type, border_color=border_color)

      return True
    
    return False
  
def highLightWords(words, text_lines, drawn_boxes, xmls_boxes, pageNum,
           field_type=None, border_color="green", after_word=None):
  
  after_word_found = True if after_word is None else False
  
  for first_line_index in range(len(text_lines)):
    first_line = text_lines[first_line_index]
    chars = []
    for elem in first_line._objs:
      if isinstance(elem, pdfminer.layout.LTChar):
        chars.append(elem)    
        
    first_line._objs = chars
    first_line_text = first_line.get_text()
    
    founded_words = []
    
    if not after_word_found:
      if after_word not in first_line_text:
        continue
      else:
        after_word_found = True

    if words[0] not in first_line_text:
      continue

    added_new_word = True
    line_index = first_line_index
    
    while added_new_word:
      added_new_word = False
      
      if line_index == len(text_lines):
        return False
      
      line = text_lines[line_index]
    
      chars = []
      for elem in line._objs:
        if isinstance(elem, pdfminer.layout.LTChar):
          chars.append(elem)    
          
      line._objs = chars
      line_text = line.get_text()
      
      position = 0
      for word in words[len(founded_words):]:
        if word in line_text:
          position = line_text.find(word, position)
          if position != -1:
            founded_words.append(word)
            added_new_word = True
          else:
            break
        else:
          break
          
      if len(words) == len(founded_words):
        if draw_words(first_line_index, line_index, 
              words, text_lines,
              drawn_boxes, xmls_boxes, pageNum,
              field_type=field_type, border_color=border_color) == True:
          return True
        else:
          break
        
      line_index += 1
  return False


def drawElement(x0, y0, x1, y1, text_value, drawn_boxes, xmls_boxes, pageNum,
        field_type=None, border_color="green"):

  bbox = (int(DPI_SCALE * x0 - 5), int(DPI_SCALE * y0 - 5) - 10000 * pageNum,
        int(DPI_SCALE * x1 + 5), int(DPI_SCALE * y1 + 5) - 10000 * pageNum)

  if not (bbox, text_value) in drawn_boxes:
    drawn_boxes.append((bbox, text_value))
    if field_type is not None:
      xmls_boxes.append({'field_type': field_type, 'text_value': text_value, 
                 'bbox': bbox, "pageNum": pageNum, "border_color": border_color})
    return True

  return False


def parse_obj(lt_objs, text_lines_to_handle):
	rawText = ''
	for text_box in lt_objs:
		if isinstance(text_box, pdfminer.layout.LTTextBoxHorizontal):
			for line in sorted(text_box._objs, key=lambda obj: obj.y1, reverse=True):
				text = line.get_text()
				if len(text) > 5:
					text_lines_to_handle.append(line)
					rawText += text[:-1]
					if text[-1:] == "\n":
						rawText += " "  
					else:
						if text[-1:] == " ":
							rawText += " "  
						else:
							rawText += text[-1:] + " "  
	return rawText


def highlightObjects(objects, field_type, text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors):
  # print("\nHighlight", field_type)
  for words in objects:
    # print(' '.join(words))
    highLightWords(words, text_lines, drawnBoxes, xmlsBoxes, pageNum,
     field_type=field_type, border_color=border_colors[field_type])

def findAndHighlight(string, field_type, processedText, text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors):
    new_highlights = [name.split(' ') for name in re.findall(string, processedText)]
    highlightObjects(new_highlights, field_type, text_lines, drawnBoxes, xmlsBoxes, pageNum, border_colors)
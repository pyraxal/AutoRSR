from importlib.machinery import SourceFileLoader
import json
import whispherx
import auto_rsr
import re
module = SourceFileLoader("bertalign", "/directory_of_bert/__init__.py").load_module()
from bertalign import Bertalign

def format(json_file):
    '''
    Formats a list and cleans up data
    '''
    a_dict = json.loads(json_file)
    a_list = a_dict.get('transcriptions', [])
    sentences = []
    for item in a_list:
        text_sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', item['transcription'])
        sentences.extend(text_sentences)
    encouragement_phrases = [
        "good job.",
        "you're doing good.",
        "well done.",
        "keep it up.",
        "nice work.",
        "excellent.",
        "great effort.",
        "fantastic.",
        "brilliant.",
        "way to go.",
        "superb.",
        "awesome.",
        "good going."
    ]
    filtered_sentences = [sentence for sentence in sentences if sentence.strip().lower() not in encouragement_phrases]
   
    return ' '.join([a+"\n" for a in filtered_sentences])
        

def jsonize(word_list):
    '''
    Converts data to a json file.  
    '''
    sentence_list = []
    for idx in range(0, len(word_list), 2):
        ground_truth = word_list[idx]
        response = word_list[idx + 1] if idx + 1 < len(word_list) else ""
        sentence_entry = {
            "id": str((idx // 2) + 1),
            "Ground Truth": ground_truth,
            "Response": response
        }
        sentence_list.append(sentence_entry)
    
    result = {"Sentences": sentence_list}
    return json.dumps(result, indent=2)

def clean_bert(reference_file, input_list):
    '''
    Cleans up the bertalign output to better represent RSR
    '''
    with open(reference_file, 'r') as ref_file:
        reference_sentences = {line.strip() for line in ref_file}

    def split_sentences(text):
        import re
        sentence_endings = re.compile(r'(?<=[.!?]) +')
        return sentence_endings.split(text.strip())

    cleaned_list = []
    i = 0
    while i < len(input_list):
        item = input_list[i].strip()
        
        if not item:
            i += 1
            continue

        sentences = split_sentences(item)
        if len(sentences) == 1:
            cleaned_list.append(item)
            i+=1
            continue

        if all(sentence in reference_sentences for sentence in sentences):
            if len(sentences) > 1:
                next_item = input_list[i + 1].strip() if (i + 1) < len(input_list) else ''
                for j, sentence in enumerate(sentences):
                    cleaned_list.append(sentence)
                    if j == 0 and next_item:
                        cleaned_list.append(next_item)
                i += 2 
            else:
                cleaned_list.append(sentences[0])
                i += 1
                
        else:
            longest_sentence = max(sentences, key=len)
            cleaned_list.append(longest_sentence)
            i += 1

    formatted_list = []
    n = len(cleaned_list)
    
    i = 0
    while i < n:
        formatted_list.append(cleaned_list[i])
        if (i + 1 < n and 
            cleaned_list[i] in reference_sentences and 
            cleaned_list[i + 1] in reference_sentences):
            if(cleaned_list[i] != cleaned_list[i + 1]):
                formatted_list.append("")
            else:
                formatted_list.append(cleaned_list[i + 1])
                i+=1
        i += 1
            
    return formatted_list

def find_lines_and_next(file1, a_list):
    '''
    More processing in preperation for final output
    '''
    with open(file1, 'r') as f1:
        lines_to_find = set(line.strip() for line in f1)

    found_lines = set()
    lines = a_list
    output_lines = []

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line in lines_to_find and stripped_line not in found_lines:
            found_lines.add(stripped_line)  
            output_lines.append(stripped_line)
            if i + 1 < len(lines):  
                output_lines.append(lines[i + 1].strip())  

        return output_lines

def transcribe(filename):
    '''
    Transcribes using whisperx
    '''
    return(whispherx.transcribe(filename))

def align(ground_truth, words):
    '''
    Uses bertalign to align. Returns a nicely formatted json. 
    '''
    src = open(ground_truth,"r").read()
    aligner = Bertalign(src, words)
    aligner.align_sents()
    lines = find_lines_and_next(ground_truth, clean_bert(ground_truth, aligner.return_sents()))
    return jsonize(lines)

'''
Sample:

json1 = whispherx.transcribe(wavfile_path)
json2 = align(gt, format(json1))
ground_truth = open(gt).readlines()
ground_truth, response = auto_rsr.prepare(json2, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
_, __, score = auto_rsr.batch(gt, response)
print(score)

'''

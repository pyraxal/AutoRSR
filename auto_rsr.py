import ftfy
import re
import json
import itertools
import copy
from collections import deque
from transformers.models.whisper import english_normalizer

def normalize(target):  
    normalizer = english_normalizer.EnglishTextNormalizer(json.loads(open("/english.json").read()))
    return(normalizer(target))

def prepare(json_str, id_list):
    '''
    Prepare a json input for processing
    '''
    a_dict = json.loads(json_str)
    id_list = [int(item) for item in id_list]
    sentences = a_dict.get("Sentences", [])
    sentences = [entry for entry in sentences if int(entry['id']) in id_list]
    ground_truth =  ([item['Ground Truth'] for item in sentences])
    response = ([item['Response'] for item in sentences])
    return ground_truth, response

def standarize(a_str):
    '''
    Standarizes text and removes utterances
    '''
    a_str = ftfy.fix_text(a_str)
    a_str = a_str.strip()
    a_str = re.sub(r'\b(?:uh|um|ah|)\b', '', a_str, flags=re.IGNORECASE)
    a_str = re.sub(r'\s+', ' ', a_str).strip()
    a_str = normalize(a_str)
    return a_str

def generate_pairs(words):
    pairs = []
    for i in range(len(words) - 1):
        pairs.append((words[i], words[i + 1], i))
    return pairs
        
def preprocess(word_list, target):
    
    '''
    Takes a word list as an input, copies it, and removes all but one instance of a repeated string(s)
    Additionally, it will also make the child's response closer to the adult by determining fusions ie: 
    bird house --> birdhouse  
    Returns the processed list and a edit sequence
    '''
    
    word_list = word_list.copy()
    n = len(word_list)
    i = 0
    edits = {"Repetition": [], "Deletion": [], "Insertion": [], "Substitution": [], "Transposition": []}
    sequences = {}
    idx_list = []

    #Repetition is checked for here
    while i < n:
        # Try to find the longest repeating sequence starting from index i
        for length in range(1, n - i):
            sequence = tuple(word_list[i:i+length])
            count = 0
            j = i

            # Count how many times the sequence repeats consecutively
            while j < n and tuple(word_list[j:j+length]) == sequence:
                count += 1
                j += length

            # Update the maximum count for this sequence
            if count > 1:
                if sequence in sequences:
                    sequences[sequence] = max(sequences[sequence], count)
                else:
                    sequences[sequence] = count

            # Move to the next sequence if it has been counted and update the ending idx of the sequence
            if count > 1:
                idx_list.append(j-1)
                i = j - length
                break
        else:
            i += 1

    #Format output as ("Repeat", sequence, # of times repeated, start idx of repeat)
    repeated_sequences = [["Repeat", list(sequence), count, idx_list.pop(0)+1-len(list(sequence)) * count] for sequence, count in sequences.items()]
    
    #Add repetitions and slices the index properly
    for element in repeated_sequences:
        edits["Repetition"].append(element)
        del word_list[element[3]:element[3]+element[2]-1]
    
    a_set = set(target)
    pairs1 = generate_pairs(word_list)

    # Check if combined pairs from str1 exist as a word in str2 and modify the list
    modified_list = word_list[:]
    i = 0

    while i < len(pairs1):
        word1, word2, index = pairs1[i]
        combined_word = word1 + word2
        if combined_word in a_set:
            modified_list[index] = combined_word
            modified_list.pop(index + 1)
            # Regenerate pairs starting from the current index
            pairs1 = generate_pairs(modified_list)
        i += 1
        
    return modified_list, edits

def modified_levenshtein_distance(word_list, word_list2, edits):
    
    '''
    Slightly modified levenshtein distance algoritmn that treats an entire word as a character.
    Takes two word lists and a edit sequence as an input and returns nothing 
    '''
   
    m, n = len(word_list), len(word_list2)
    d = [[0] * (n + 1) for _ in range(m + 1)]
   
    # Initialize the matrix
    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j
   
    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word_list[i - 1] == word_list2[j - 1]:
                d[i][j] = d[i - 1][j - 1]        
            else:
                d[i][j] = min(
                    d[i - 1][j] + 1,    # Deletion
                    d[i][j - 1] + 1,    # Insertion
                    d[i - 1][j - 1] + 1 # Substitution
                )
   
    # Traceback to find the edit sequence
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and word_list[i - 1] == word_list2[j - 1]:
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or d[i][j] == d[i - 1][j] + 1):
            edits["Deletion"].append(["Delete", word_list[i - 1], i - 1])
            i -= 1
        elif j > 0 and (i == 0 or d[i][j] == d[i][j - 1] + 1):
            edits["Insertion"].append(["Insert", word_list2[j - 1], i])
            j -= 1
        else:
            edits["Substitution"].append(["Substitute", word_list[i - 1], word_list2[j - 1], i - 1])
            i -= 1
            j -= 1
       
def calculate_match_rate(list1, list2):
    return sum(1 for a, b in zip(list1, list2) if a == b)

def pad_list(target, input_list):
    best_match_rate = -1
    best_padded_list = None
    best_position = -1
    for i in range(len(target) + 1):
        padded_list = input_list[:i] + [""] + input_list[i:]
        match_rate = calculate_match_rate(target, padded_list)
        if match_rate > best_match_rate:
            best_match_rate = match_rate
            best_padded_list = padded_list
            best_position = i
    return best_padded_list, best_position

def swap_elements_bfs(target, input_list):
    initial_match_rate = calculate_match_rate(target, input_list)
    queue = deque([(input_list, [], initial_match_rate)])
    visited = set()
    best_sequence = []
    best_list = input_list.copy()
    best_match_rate = initial_match_rate

    while queue:
        current_list, swaps, match_rate = queue.popleft()

        if tuple(current_list) in visited:
            continue

        visited.add(tuple(current_list))

        if match_rate > best_match_rate:
            best_match_rate = match_rate
            best_sequence = swaps.copy()
            best_list = current_list.copy()

        if match_rate == len(target):
            break

        for i in range(len(target)):
            for j in range(i + 1, len(target)):
                if (target[i] == current_list[j] and current_list[i] != "") or (target[j] == current_list[i] and current_list[j] != ""):
                    new_list = current_list.copy()
                    new_list[i], new_list[j] = new_list[j], new_list[i]
                    new_swaps = swaps + [["Transpose", new_list[i], new_list[j], i, j]]
                    new_match_rate = calculate_match_rate(target, new_list)
                    if new_match_rate >= match_rate:
                        queue.append((new_list, new_swaps, new_match_rate))

    return best_sequence, best_list

def update_transpositions(transpositions, padding_index):
    new_index = 0
    for i in range(len(padding_index)):
        if padding_index[i] == "":
            continue
        for transposition in transpositions:
            if transposition[3] == i:
                transposition[3] = new_index
            if transposition[4] == i:
                transposition[4] = new_index
        new_index += 1

def transpose(target, input_list, edits):
    '''
    Forcefully checks for transpositions, only works when length difference is 1 or 0. 
    '''
    if len(target) > len(input_list):
        input_list, _ = pad_list(target, input_list)
    elif len(target) < len(input_list):
        target, _ = pad_list(input_list, target)
        target, input_list = target, input_list

    swaps, aligned_list = swap_elements_bfs(target, input_list)
    update_transpositions(swaps, input_list)
    aligned_list = [item for item in aligned_list if item != '']
    
    edits["Transposition"] = swaps

    return aligned_list

def transpose2(a_dict):   
    '''
    Takes a word list and edit sequence and detects substitutions that are actually transpositions and converts them.
    '''

    #Generates a graph in adjacency list representation
    graph = {}
    a_list = a_dict['Substitution']
    for element in a_list:
        addEdge(graph, element[1], element[2])
        
    #DFS returns all possible paths, then we filter only the paths that returns a cycle, which then we slice in half 
    cycles = [[node]+ path for node in graph for path in dfs(graph, node, node)][::2] 

    for element in cycles:
        #Find substitute pairs and replaces them with a single transposition
        element_to_modify = element[0:2]
        element_to_remove = element[1:]
        element1 = []
        element2 = []
        flag = True
        flag2 = True
        for item in a_list:
            if element_to_modify == item[1:3] and flag == True:
                element1 = item
                flag == False
                
            if element_to_remove == item[1:3] and flag2 == True:
                element2 = item
                flag == False
            
            if flag == False and flag2 == False:
                break
        
        a_dict["Transposition"].append(['Transpose', element1[1], element2[1], element1[3], element2[3]])
        a_list.remove(element1)
        a_list.remove(element2)    
       
    
def addEdge(graph,u,v): 
    if u in graph:
        graph[u].append(v)
    else:
        graph[u] = [v]
  
def dfs(graph, start, end):
    '''
    Basic DFS using stacks
    '''
    master = [(start, [])]
    while master:
        state, path = master.pop()
        if path and state == end:
            yield path
            continue
        if state in graph: 
            for next_state in graph[state]:
                if next_state in path:
                    continue
                master.append((next_state, path+[next_state]))

def word_list(sentence):
    '''
    Splits a string into its list of words.
    Returns that list of words
    '''
    return sentence.split()

def score(edits):
    '''
    Takes a edit sequence and returns a RSR score. No context parsing ATM, only basic counting
    '''
    score = 0
    for key in edits:
        score += len(edits[key])

    return score

def batch(ground_truth, response):
    '''
    Batch processes and batch scores an entire RSR session. Takes the filename for groundtruth as the first
    input and the filename for the RSR audio as the second
    '''
    edit_sequences = []
    word_lists = []
    score_list = []
    ground_truth = [standarize(item) for item in ground_truth]
    test_list = [standarize(item) for item in response]
    
    for target, response in itertools.zip_longest(ground_truth, test_list, fillvalue=''):
        target = word_list(target)
        response = word_list(response)
        word_lists.append(response)
        processed, edit_sequence = preprocess(response, target)
        
        #will get every transposition if the length difference is less than 1.
        #however, the algorithm im using is not scalable to greater length differences
        if(abs(len(target) - len(processed)) <= 1):
            edits = copy.deepcopy(edit_sequence)
            original = processed.copy()
            modified_levenshtein_distance(original, target, edits)
            transposed = transpose(target, processed, edit_sequence)
            modified_levenshtein_distance(transposed, target, edit_sequence)
            if(score(edit_sequence) < score(edits)):
                edit_sequences.append(edit_sequence)
                score_list.append(score(edit_sequence))
            else:
                edit_sequences.append(edits)
                score_list.append(score(edits))
        
        #will only get transpositions that are substitute substitute pairs
        else:
            modified_levenshtein_distance(processed, target, edit_sequence)
            transpose2(edit_sequence)
            edit_sequences.append(edit_sequence)
            score_list.append(score(edit_sequence))
    
    return word_lists, edit_sequences, score_list





    

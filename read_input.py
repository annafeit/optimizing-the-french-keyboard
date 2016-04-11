import codecs
import pandas as pd
import unicodedata
import numpy as np

#File names for input values
_keyslots_file = 'input\\variable_slots.txt'
_letter_file = 'input\\letters.txt'
_character_file = 'input\\characters.txt'
_azerty_file = "input\\azerty.csv"
_similarity_c_c_file = 'input\\similarity_c_c_binary.xlsx'
_similarity_c_l_file = 'input\\similarity_c_l_binary.xlsx'
_distance_file = "input\\distance.xlsx"
_frequency_letter_file = "input\\frequency_letters_bepo.csv"
_frequency_bigram_file = "input\\frequency_bigrams_bepo.csv"
_ergonomics_file = "input\\ergonomics.csv"
_performance_file = "input\\performance.csv"

def get_azerty():
    """
        Returns the Azerty keyboard in form of a dict from characters to keyslots (=mapping)
    """
    azerty =  pd.read_csv(_azerty_file, index_col=1, sep="\t", encoding='utf-8', quoting=3)
    azerty.index=azerty.index.str.strip()
    azerty = azerty.to_dict()["keyslot"]
    return azerty

def get_characters():
    """
        Returns a list of to-be-mapped characters
    """
    with codecs.open(_character_file, encoding='utf-8') as f:
        characters_file = f.read().splitlines()
    characters = [c.strip() for c in characters_file]
    return characters

def get_letters():
    """
        Returns a list of letters in relation to which character mapping should be optimized
    """        
    with codecs.open(_letter_file, encoding='utf-8') as f:
        letters_file = f.read().splitlines()
    letters = [c.strip() for c in letters_file]
    return letters

def get_keyslots():    
    """
        Returns a list of keyslots that are free for characters to be mapped to. 
        Reads the correspoinding input file and removes all keyslots defined to be fixed in "numbers.csv"
    """
    with codecs.open(_keyslots_file, encoding='utf-8') as f:    
        keyslots_file = f.read().splitlines()
    keyslots = [c.strip() for c in keyslots_file]    
    
    numbers = pd.read_csv(_keyslots_file, index_col=1, sep="\t", encoding='utf-8', quoting=3)
    numbers.index=numbers.index.str.strip()
    numbers = numbers.to_dict()["keyslot"]
    
    for n_slot in numbers.values():        
        keyslots.remove(n_slot)
        
    return keyslots

def get_character_similarities():
    """
        Returns a dictionary of character tuples to similarity values between the two characters
        Reads the corresponding similarity matrix but removes the characters and letters not given in the corresponding lists
        The dictionary only contains similarity values for those pairs whose similarity is defined to be >0
    """
    characters = get_characters()
    letters = get_letters()
    similarity_c_c = _read_similarity_matrix(_similarity_c_c_file, characters, letters)
    return similarity_c_c

def get_character_letter_similarities(): 
    """
        Returns a dictionary of character-letter tuples to similarity values between each character and each letter
        Reads the corresponding similarity matrix but removes the characters and letters not given in the corresponding lists
        The dictionary only contains similarity values for those pairs whose similarity is defined to be >0
    """
    characters = get_characters()
    letters = get_letters()
    similarity_c_l = _read_similarity_matrix(_similarity_c_l_file, characters, letters)
    return similarity_c_l

def get_distances(level_cost):
    """
        Returns a dictionary of key tuples to distance values between the keys. 
        Returns two such dictionaries, one where the distance is based on the row and column distance, 
        one where it also includes the distance due to different levels (Shift, Alt etc.) The additional level cost is given as input.
    """
    #Distance values (key,key)->d
    distance_level_0, distance_level_1 = _read_distance_matrix(_distance_file, level_cost, recompute=0)
    return distance_level_0, distance_level_1

def get_probabilities():
    """
        Returns the letter and bigram level probabilities in form of a dictionary. 
        Both contain the frequencies of both, letters and characters, as well as letter-character and character-character pairs
        TODO: what do we do with accent + space?
    """
    #TODO: adapt probabilities of composable characters to character list. 
    #if letter uses accent and accented letter is not in character list, add to probability of dead key. 
    # Also use this to give warning if a certain character is not in character list but in input list
    characters = get_characters()
    letters = get_letters()
    all_chars = characters + letters
    
    #1. read the frequencies from the corresponding files as they are
    p_single = pd.read_csv(_frequency_letter_file, sep=" ", encoding="utf-8", index_col=0, quoting=3)
    p_single = p_single.to_dict()[u'frequency']
    
    p_bigrams_all = _read_tuple_list_to_dict(_frequency_bigram_file)
    
    #2. go through characters and letters and check if they are available in dict. If not add 0 probability. 
    # For each deadkey in the character list, sum up the probabilities of letters composed with the deadkey
    for c1 in all_chars:
        #single letter probabilities
        if not c1 in p_single:
            if c1[-1] == "d":
                #deadkey: sum up all character frequencies composed of this deadkey and not in characters
                c1_p = 0
                for k in p_single.keys():
                    if not k in all_chars:                       
                        if  _is_composed_of(c1[0], k):
                            #add this letter's probability to deadkey probability
                            print c1 +" composes "+k
                            c1_p += p_single[k]
                p_single[c1] = c1_p
            else:
                #add 0
                p_single[c1] = 0
    #Normalize again
    s = np.sum(p_single.values())
    p_single_normalized = {c: v/float(s) for c, v in p_single.iteritems()}
    
    #3. go through bigrams and correct them accordign to the given characters, 
    #that is letter pairs with accented characters need to be distributed to other letter pairs accoridng to the 
     #keypresses that needed to be made.  
    p_bigrams = {}
    for (c1,c2) in p_bigrams_all.keys():
        if c1 in all_chars and c2 in all_chars:
            p_bigrams[(c1,c2)] = p_bigrams_all[(c1,c2)]
        else:
            c1_d = _decompose(c1)
            c2_d = _decompose(c2)

            #check if c1 is a fixed letter or to-be-mapped character. If not check its decomposition.
            if not c1 in all_chars:
                #check if its a composed letter. If not we don't care about it
                if len(c1_d)>1:                
                    c1_1 = c1_d[0]                
                    c1_2 = c1_d[1]         
                    #store bigram for the composition, if they are in the list. Else ignore.
                    if c1_1 in all_chars and c1_2 in all_chars:
                        if (c1_1, c1_2) in p_bigrams:
                            p_bigrams[(c1_1, c1_2)] += p_bigrams_all[(c1, c2)]
                        else:
                            p_bigrams[(c1_1, c1_2)] = p_bigrams_all[(c1, c2)]
                            
                    #now check transition to second letter
                    if len(c2_d) == 1 and c2_d in all_chars:
                        if (c1_2, c2) in p_bigrams:
                            p_bigrams[(c1_2, c2)] += p_bigrams_all[(c1, c2)]
                        else:
                            p_bigrams[(c1_2, c2)] = p_bigrams_all[(c1, c2)]
                    elif len(c2_d)>1:
                        #decompose again
                        c2_1 = c2_d[0]                
                        c2_2 = c2_d[1]  
                        #add transition c1_2 - c2_1:
                        if c1_2 in all_chars and c2_1 in all_chars:
                            if (c1_2, c2_1) in p_bigrams:
                                p_bigrams[(c1_2, c2_1)] += p_bigrams_all[(c1, c2)]
                            else:
                                p_bigrams[(c1_2, c2_1)] = p_bigrams_all[(c1, c2)]
                        # add transition c2_1 - c2_2:
                        if c2_1 in all_chars and c2_2 in all_chars:
                            if (c2_1, c2_2) in p_bigrams:
                                p_bigrams[(c2_1, c2_2)] += p_bigrams_all[(c1, c2)]
                            else:
                                p_bigrams[(c2_1, c2_2)] = p_bigrams_all[(c1, c2)]
                else:
                    print "We don't care about", c1
            elif not c2 in all_chars:
                if len(c2_d)>1:
                    c2_1 = c2_d[0]                
                    c2_2 = c2_d[1]  
                    #add transition c1 - c2_1:
                    if c1 in all_chars and c2_1 in all_chars:
                        if (c1, c2_1) in p_bigrams:
                            p_bigrams[(c1, c2_1)] += p_bigrams_all[(c1, c2)]
                        else:
                            p_bigrams[(c1, c2_1)] = p_bigrams_all[(c1, c2)]
                        # add transition c2_1 - c2_2:
                        if c2_1 in all_chars and c2_2 in all_chars:
                            if (c2_1, c2_2) in p_bigrams:
                                p_bigrams[(c2_1, c2_2)] += p_bigrams_all[(c1, c2)]
                            else:
                                p_bigrams[(c2_1, c2_2)] = p_bigrams_all[(c1, c2)]
                else:
                    print "We don't care about", c2
    s = np.sum(p_bigrams.values())
    p_bigrams_normalized = {(c1,c2): v/float(s) for (c1,c2), v in p_bigrams.iteritems()}
                
                
            
    
    return p_single_normalized, p_bigrams_normalized

def get_ergonomics():
    """
        Returns a dictionary with letter-character tuples to ergonomic values
    """
    ergonomics = _read_tuple_list_to_dict(_ergonomics_file)
    return ergonomics

def get_performance():
    """
        Returns a dictionary with letter-character tuples to performance values
    """
    #Performance: (key, letter)->t
    performance = _read_tuple_list_to_dict(_performance_file)
    return performance 

def _decompose(c):
    c_d = unicodedata.normalize('NFKD', c)
    special_char_list = {"^": "0302", "~":"0303"}
    for i in range(0,len(c_d)):
        if c_d[i] in special_char_list:
            c_d[i] = special_char_list[c_d[i]]
    return c_d
        
def _read_distance_matrix(path, level_cost, recompute=0):
    """
        reads the distance between the keys from the excel file. If the file is empty (or recompute is set) it creates the distance matrix
        and writes it to the file. The file does not include any level distance.
        Distance is defined as the sum of the vertical and horizontal distance.         
        
        level_cost: dict
            additional cost for each lower level, e.g. level_cost = {'':0, 'Shift':1, 'Alt':2, 'Alt_Shift':3}, 
            is computed in relation to each other, 
            that is cost is 1 if one character on Shift, the other on Alt level. Cost is 2 if one character on single, other
            on Alt level
        recompute: boolean
            If recompute=1 it recomputes the distances between the keys in the index of matrix and saves them to the given file. 
            
        outputs 2 dictionaries from key-tuple to distance.
        dictionary_level_0: normalized distance not including any level cost
        dictionary_level_1: normalized distance including the level cost
    """
    row_numbers = {u"A":0, u"B":1, u"C":2, u"D":3, u"E":4}
    df = pd.read_excel(path, encoding='utf-8')
    index = df.index
    columns = df.columns
    dictionary_level_0 = {}
    dictionary_level_1 = {}
    changed = 0
    for i in range(0,len(index)): #row index
        for j in range(0, len(columns)): #column index
            slot1 = index[i]
            slot2 = columns[j]            
            if recompute or pd.isnull(df.iloc[i,j]):                
                #if there is no value yet, compute it based on the names:
                row_distance = np.abs(row_numbers[slot1[0]] - row_numbers[slot2[0]])
                column_distance = np.abs(int(slot1[1:3]) - int(slot2[1:3]))                
                #Special case: shift
                if slot1[0:3] == "A03":
                    if int(slot2[1:3])>3:
                        column_distance = max(0,column_distance-4)
                if slot2[0:3] == "A03":
                    if int(slot1[1:3])>3:
                        column_distance = max(0,column_distance-4)
                df.iloc[i,j] = row_distance+column_distance
                changed = 1
                
            level_distance = np.abs(level_cost[slot1[4:]] - level_cost[slot2[4:]])
            #add level cost and normalize
            dictionary_level_1[(slot1,slot2)] = (df.iloc[i,j]+level_distance) / float((df.max().max() + np.max(level_cost.values())))
            dictionary_level_0[(slot1,slot2)] = df.iloc[i,j] / float((df.max().max()))
    if changed:
        df.to_excel(path)                                  
    return dictionary_level_0, dictionary_level_1


def _read_similarity_matrix(path, characters, letters):
    """
        Reads the given matrix into a dictionary of the form (c1,c2)->similarity
        Filters out all characters that are not in the given character list
        Already normalized
    """    
    df = pd.read_excel(path, encoding='utf-8')
    df.index=df.index.str.strip()
    df.columns=df.columns.str.strip()
    index = df.index
    columns = df.columns
    dictionary = {}
    for i in range(0,len(df)): #row index
        for j in range(0, len(df.columns)): #column index
            row = index[i]
            col = columns[j]
            if (row in characters and col in characters) or (row in characters and col in letters):
                if not pd.isnull(df.iloc[i,j]):
                    dictionary[(row,col)] = df.iloc[i,j]
    return dictionary

def _read_tuple_list_to_dict(path):
    """
        Reads a file into a dictionary. 
        The file must have the following format:
        key1 key2 value
        Then the dictionary is of the form:
        {(key1,key2):value}
    """
    with codecs.open(path, 'r', encoding="utf-8") as bigram_file:
        all_lines = bigram_file.readlines()
        lines = [l.rstrip() for l in all_lines]
        #create dict
        p_bigrams = {}
        for l in lines:
            parts = l.split(" ")
            p_bigrams[(parts[0], parts[1])] = float(parts[2])
    return p_bigrams

def _is_composed_of(deadkey, character):
    """
        checks if the given character is a composed character and if it is composed with the given deadkey
    """
    if not character == "space":
        special_char_list = {"^": "0302", "~":"0303"}
        if len(character)>1:
            #has multiple characters in it, check if the deadkey is somehwere in there
            for c in character:
                res = _is_composed_of(deadkey,c)
                if res:
                    return res
        if unicodedata.decomposition(character) == "":
            return 0
        else:
            if deadkey in special_char_list:
                deadkey_code = special_char_list[deadkey]
            else:
                deadkey_code = unicodedata.decomposition(deadkey)[-4:]
            character_code = unicodedata.decomposition(character)[-4:]
            return deadkey_code == character_code
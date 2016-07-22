# -*- coding: utf-8 -*-
import codecs
import pandas as pd
import unicodedata
import numpy as np

PYTHONIOENCODING="utf-8"

_keyslots_file = ""
_numbers_file = ""
_letter_file = 'input/letters.txt'
_character_file = ""
_azerty_file = "input/layouts/azerty.csv"
_similarity_c_c_file = 'input/similarity_c_c_binary_m.xlsx'
_similarity_c_l_file = 'input/similarity_c_l_m.xlsx'
_distance_file = "input/distance.xlsx"
_frequency_letter_file = ""
_frequency_bigram_file = ""
_ergonomics_file = "input/ergonomics_antti.csv"
_performance_file = "input/performance.csv"
    
def set_scenario_files(scenario):
    #File names for input values 
    global _keyslots_file
    _keyslots_file = 'input/variable_slots_'+scenario+'.txt'
    
    global _numbers_file
    _numbers_file= 'input/numbers_'+scenario+'.csv'
    
    global _character_file
    _character_file= 'input/characters_'+scenario+'.txt'
    
    global _frequency_letter_file
    _frequency_letter_file= "input/frequency_letters_"+scenario+'.txt'
   
    global _frequency_bigram_file
    _frequency_bigram_file= "input/frequency_bigrams_"+scenario+'.txt'




#the unicode keycodes for the diacritic characters, just to be sure the decomposition recognizes them correctly
unicode_diacritic = {u"\u0302": u"^d",
                     u"\u0308": u"¨d",
                     u"\u0303": u"~d",
                     u"\u0306": u"˘d",
                     u"\u030c": u"ˇd",
                     u"\u0311": u"̑d",
                     u"\u0300": u"ˋd",
                     u"\u0301": u"´d",
                     u"\u0304": u"ˉd",
                     u"\u0331": u"_d",
                     u"\u0307": u"˙d",
                     u"\u0323": u".d",
                     u"\u030a": u"°d",
                     u"\u030b": u"˝d",
                     u"\u030f": u"˵d",              
                     u"\u0327": u"¸d",
                     u"\u0328": u"˛d",
                     u"\u0326": u",d",
                     u"\u0335": u"-d",
                     u"\u0337": u"/d"
                    }
def get_unicode_diacritic(u):
    if u in unicode_diacritic.keys():
        return unicode_diacritic[u]
    else:
        return u

diacritic_unicode = {u"^": u"\u0302", u"ˆ": u"\u0302",
                     u"¨": u"\u0308",
                     u"~": u"\u0303", u"˜": u"\u0303", 
                     u"˘": u"\u0306",
                     u"ˇ": u"\u030c",
                     u"̑": u"\u0311",
                     u"ˋ": u"\u0300", u"`": u"\u0300", 
                     u"ˊ": u"\u0301", u"´": u"\u0301", 
                     u"ˉ": u"\u0304", 
                     u"_": u"\u0331", u"̲":u"\u0331",
                     u"˙": u"\u0307",
                     u".": u"\u0323",
                     u"°": u"\u030a",
                     u"˝": u"\u030b",
                     u"˵": u"\u030f", u"̏": u"\u030f",                     
                     u"¸": u"\u0327",
                     u"˛": u"\u0328",
                     u",": u"\u0326", u"̦": u"\u0326", 
                     u"-": u"\u0335", u"̵": u"\u0335",
                     u"/": u"\u0337", u"̷": u"\u0337"
                    }

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
    characters = [correct_diacritic(c.strip()) for c in characters_file]      
    return characters

def correct_diacritic(c):
    """
    Checks if the given character represents a diacritic mark and if so turns it into the common representation of the diacritic mark as 
    given by the unicode_diacritic dict defined above. Otherwise returns the characters as is
    """
    new_c = c
    if len(c)==2 and "d" in c: #diacritic
        if c[0] in unicode_diacritic:
            new_c = unicode_diacritic[c[0]]
        else:
            new_c = unicode_diacritic[diacritic_unicode[c[0]]] #correct to a simple representation of the diacritic mark        
    return new_c

def get_letters():
    """
        Returns a list of letters in relation to which character mapping should be optimized
    """        
    with codecs.open(_letter_file, encoding='utf-8') as f:
        letters_file = f.read().splitlines()
    letters = [c.strip() for c in letters_file]
    return letters

def get_fixed_characters():
    """
        Returns a list of characters that are fixed on the keyboard. Their corresponding slots cannot be filled, but the
        to-be-mapped characters are not optimized in relation to those but they are simply ignored.
    """    
    fixed = pd.read_csv(_numbers_file, index_col=1, sep="\t", encoding='utf-8', quoting=3)
    fixed = fixed.index.tolist()
    return [correct_diacritic(c.strip()) for c in fixed]   
    
def get_keyslots():    
    """
        Returns a list of keyslots that are free for characters to be mapped to. 
        Reads the correspoinding input file and removes all keyslots defined to be fixed in "numbers.csv"
    """
    with codecs.open(_keyslots_file, encoding='utf-8') as f:    
        keyslots_file = f.read().splitlines()
    keyslots = [c.strip() for c in keyslots_file]    
    
    numbers = pd.read_csv(_numbers_file, index_col=1, sep="\t", encoding='utf-8', quoting=3)
    numbers = numbers.to_dict()["keyslot"]
    
    for n_slot in numbers.values(): 
        try:
            keyslots.remove(n_slot)
        except ValueError:
            #do nothing
            continue
            
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
    
    p_single = pd.read_csv(_frequency_letter_file, sep=" ", encoding="utf-8", index_col=0, quoting=3)
    p_single = p_single.to_dict()[u'frequency']
    
    p_bigrams = _read_tuple_list_to_dict(_frequency_bigram_file)
    
    return p_single, p_bigrams

    
def derive_probabilities_from_raw_values(letter_file, bigram_file, scenario=""):
    """
        Derives the letter and bigram level probabilities from the given raw probability files for *all* characters and bigrams
        Takes care of combined characters and distributing the frequencies accordingly. Then writes them to a file for later use.
        Both contain the frequencies of both, letters and characters, as well as letter-character and character-character pairs
        The letters and characters that have no frequency available, get half of the lowest frequency 
        At the end writes the frequencies to the corresponding scenario file in the input folder.
        
    """
    if scenario != "":
        set_scenario_files(scenario)
    all_chars = get_characters() + get_letters() + get_fixed_characters()        
    #1. read the frequencies from the corresponding files as they are
    p_single_all = pd.read_csv(letter_file, sep=" ", encoding="utf-8", index_col=0, quoting=3)
    p_single_all = p_single_all.to_dict()[u'frequency']
    p_single = {c:0 for c in all_chars}
    
     #-------------- SINGLE ------------------------
    #Go through all symbols in the given frequency list. If the symbol is in the character list, add its frequency to the one 
    #in the probability list. If not check if it is a composed character. If yes and the diacritic mark is in the character list, 
    #add its frequency to the frequency of the corresponding characters (character + diacritic mark)
    for c, v in p_single_all.items():
        c = correct_diacritic(c) #in case this is a wrong form of a "d" annotated diacritic
        if c in p_single.keys():
            p_single[c] += v
        else:
            c_dec = decompose(c)
            if len(c_dec) > 1:
                #it's a composed character, take it apart and add the frequency to the frequency of its components
                if c_dec[1] in unicode_diacritic.keys():
                    diacritic = unicode_diacritic[c_dec[1]]
                    
                    if diacritic in p_single.keys():
                        p_single[diacritic] += v
                letter = c_dec[0]
                if letter in p_single.keys():
                    p_single[letter] += v
            elif c in diacritic_unicode.keys():
                #it's a single form of the diacritic mark, e.g. ~. Add frequency to diacritic and to space
                diacritic = unicode_diacritic[diacritic_unicode[c]]
                p_single[diacritic] += v
                p_single["space"] += v            
            #else it's a character we don't care about
                
    minimum = np.min([v for v in p_single.values() if v>0])
    #Check if any of the values remained 0:
    for c, v in p_single.items():
        if v==0:
            print(u"No frequency for %s"%c)
            #p_single[c] = 0.5*minimum         
    
    #Normalize again
    s = np.sum(p_single.values())
    p_single_normalized = {c: v/float(s) for c, v in p_single.items()}        
            
    
    #-------------- BIGRAM ------------------------
    #3. go through bigrams and correct them according to the given characters, 
    #that is letter pairs with accented characters need to be distributed to other letter pairs accoridng to the 
     #keypresses that needed to be made.  
    p_bigrams_all = _read_tuple_list_to_dict(bigram_file)
    p_bigrams = {(c1,c2):0 for c1 in all_chars for c2 in all_chars}
    print(all_chars)
    print((u"r", u"Μ") in p_bigrams.keys())
    counter=0
    for (c1,c2), v in p_bigrams_all.items():        
        counter+= 1
        if (counter % 5000 == 0):
            print("%i of %i"%(counter, len(p_bigrams_all)))
        c1 = correct_diacritic(c1)
        c2 = correct_diacritic(c2)
        if (c1,c2) in p_bigrams.keys():
            p_bigrams[(c1,c2)] += v
        else:
            if len(c1)==2 and "d" in c1: #strip off "d"
                  c1 = c1[0]
            if len(c2)==2 and "d" in c1: #strip off "d"
                  c2 = c2[0]
            if c1 in diacritic_unicode.keys():                  
                #it's a single form of the diacritic mark, e.g. ~, which needs to be produced by the bigram ~ + space
                diacritic = unicode_diacritic[diacritic_unicode[c1]] #get the right diacritic
                p_bigrams[(diacritic, "space")] += v
                
                #test the same for c2
                if c2 in diacritic_unicode.keys(): 
                    diacritic2 = unicode_diacritic[diacritic_unicode[c2]] #get the right diacritic
                    p_bigrams[("space", diacritic2)] += v
                    p_bigrams[(diacritic2, "space")] += v
                elif c2 in all_chars:
                    p_bigrams[("space", c2)] += v
            elif c2 in diacritic_unicode.keys(): 
                diacritic2 = unicode_diacritic[diacritic_unicode[c2]] #get the right diacritic
                p_bigrams[("space", diacritic2)] += v
                if c1 in all_chars:
                    p_bigrams[(c1, "space")] += v
            else:
                c1_d = decompose(c1)
                c2_d = decompose(c2)

                
                if not c1 in all_chars:  #if the decomposable characters doesn't get its own key
                    #check if its a composed letter. If not we don't care about it
                    if len(c1_d)>1:                
                        c1_1 = get_unicode_diacritic(c1_d[0])
                        c1_2 = get_unicode_diacritic(c1_d[1])         
                        #store bigram for the composition, if they are in the list. Else ignore.
                        if c1_1 in all_chars and c1_2 in all_chars:
                            p_bigrams[(c1_1, c1_2)] += v
                            
                        #now check transition to second letter
                        if c2 in all_chars and c1_2 in all_chars:
                            p_bigrams[(c1_2, c2)] += v
                            
                        elif len(c2_d)>1:
                            #decompose again
                            c2_1 = get_unicode_diacritic(c2_d[0])
                            c2_2 = get_unicode_diacritic(c2_d[1])
                            #add transition c1_2 - c2_1:
                            if c1_2 in all_chars and c2_1 in all_chars:
                                p_bigrams[(c1_2, c2_1)] += v
                                
                            # add transition c2_1 - c2_2:
                            if c2_1 in all_chars and c2_2 in all_chars:
                                p_bigrams[(c2_1, c2_2)] += v
                                
                    #else:
                        #print "We don't care about", c1
                elif not c2 in all_chars: #if the decomposable characters doesn't get its own key
                    if len(c2_d)>1:
                        c2_1 = get_unicode_diacritic(c2_d[0])
                        c2_2 = get_unicode_diacritic(c2_d[1])
                        #add transition c1 - c2_1:
                        if c1 in all_chars and c2_1 in all_chars:
                            p_bigrams[(c1, c2_1)] += v
                            
                        # add transition c2_1 - c2_2:
                        if c2_1 in all_chars and c2_2 in all_chars:
                            p_bigrams[(c2_1, c2_2)] += v
                                
                    #else:
                        #print "We don't care about", c2
    
    # Give 0.5* lowest probability to those pairs that have no frequency
    minimum = np.min([v for v in p_bigrams.values() if v>0])
    for (c1,c2),v in p_bigrams.items():
        if v==0:
            print(u"No frequency for (%s, %s)"%(c1,c2))
            #p_bigrams[c1,c2] = 0.5*minimum
                  
    # normalize
    s = np.sum(p_bigrams.values())
    p_bigrams_normalized = {(c1,c2): v/float(s) for (c1,c2), v in p_bigrams.items()}
                
        
    #Write BIGRAMS  to file
    f = codecs.open(_frequency_bigram_file,'w', encoding="utf-8")    
    for (c1,c2),v in p_bigrams.items():
        f.write("%s %s %s"%(c1,c2,repr(float(v))))
        f.write("\n")
    f.close()

    #Write LETTERS  to file
    f = codecs.open(_frequency_letter_file,'w', encoding="utf-8")
    f.write("letter frequency\n")
    for c,v in p_single.items():
        f.write("%s %s"%(c,repr(v)))
        f.write("\n")
    f.close()
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

def decompose(c):
    try:
        #print c
        c_d = unicodedata.normalize('NFKD', c)
    
        return c_d
    except:
        return c
        
        
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
            #correct diacritic mark
            row = correct_diacritic(row)
            col = correct_diacritic(col)
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
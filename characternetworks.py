#!/usr/bin/env python

# # -*- coding: utf-8 -*-

# 1. IMPORTS

from collections import Counter
import itertools 
import networkx as nx
from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities
from networkx.algorithms.community.centrality import girvan_newman
from networkx.algorithms.community import kernighan_lin_bisection
from networkx.algorithms.community import label_propagation_communities
from networkx.algorithms.community import asyn_lpa_communities
from networkx.algorithms.community import k_clique_communities
import matplotlib.pyplot as plt
import re
import pandas as pd
import os
import glob
import sys
import errno
import csv
import math
from operator import itemgetter
#import community
import ucto 


# 2. CLASS CHARACTER

class Character:

    """ A character in a novel with the following properties:

    Attributes:
        book_id: An integer representing the number of the book on the Libris list (aplhabetically ordered)
        character_id: An integer representing the number of the character in the book (hierarhically ordered)
        name: A string representing the name of the character
        gender: An integer representing a code for gender (1 = male, 2 = female)
        descent_country: An integer representing a code for country of birth (1 = Nederlands, 2 = Belgie, 3 = Europees, 4 = Westers 5 = Midden Oosten 6 = Overig)
        descent_city: An integer representing a code for city of birth (1 = Amsterdam, 2 = Randstad, 3 = Buiten de Randstad, 4 = Grote stad in Vlaanderen (Brussel/ Antwerpen/ Gent), 5 = Elders in Belgie, 6 = Grote stad in Europa, 7 = elders in Europa, 8 = Stad in Midden Oosten, 9 = Dorp in Midden Oosten, 10 = Stad in VS, 11 = Dorp in VS, 12 = Stad Elders, 13 = Dorp elders)
        living_country: An integer representing a code for country of residency (1 = Nederlands, 2 = Belgie, 3 = Europees, 4 = Westers 5 = Midden Oosten 6 = Overig)
        living_city: An integer representing a code for city of residency  (1 = Amsterdam, 2 = Randstad, 3 = Buiten de Randstad, 4 = Grote stad in Vlaanderen (Brussel/ Antwerpen/ Gent), 5 = Elders in Belgie, 6 = Grote stad in Europa, 7 = elders in Europa, 8 = Stad in Midden Oosten, 9 = Dorp in Midden Oosten, 10 = Stad in VS, 11 = Dorp in VS, 12 = Stad Elders, 13 = Dorp elders)
        age: An integer representing a code for age (1 = <25, 2 = 26-35, 3 = 36-45, 4= 46-55, 5 = 56-64, 6 = 65+)
        education: An integer representing a code for education (1= highly educated, 2= lowly educated)
        profession: A string representing a profession
    """




    def __init__(self, book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession):
        self.namevariants = []
        self.book_id = book_id
        self.character_id = character_id
        self.name = name
        self.gender = gender
        self.descent_country = descent_country
        self.descent_city = descent_city
        self.living_country = living_country
        self.living_city = living_city
        self.age = age
        self.education = education
        self.profession = profession
        self.isfirstperson = False

        self.descent_recode = ''

        self.marked_name = list(self.name) 
        self.marked_name = '|'.join(self.marked_name)
        self.namecode = self.book_id+'_'+self.character_id+'_'+self.marked_name.replace(' ','+++') # DOES THIS MATCH THE NAMECODE IN def replace_namvariants?

        self.degree = 0
        self.betweenness = 0
        self.closeness = 0
        self.eigenvector = 0
        self.katz = 0
        



    def addnamevariant(self,name_variant):
        """ Adds namevariant of Character object to namevariants (= list)

        """
        self.namevariants.append(name_variant)

        
    

# 2.1. SUBCLASS Character_Centrality

class Character_Centrality(Character):
    def __init__(self, book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession, degree, betweenness, closeness, eigenvector, katz):
        Character.__init__(self, book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession)
        self.degree = degree
        self.betweenness = betweenness
        self.closeness = closeness
        self.eigenvector = eigenvector
        self.katz = katz

        self.conflictscore = {}
        self.conflictscore['degree'] = 0
        self.conflictscore['betweenness'] = 0
        self.conflictscore['closeness'] = 0
        self.conflictscore['eigenvector'] = 0
        self.conflictscore['katz'] = 0

  



# 3. CLASS BOOKS 


class Book:

    """ A novel with the following properties:

    Attributes: 
        book_id = An integer representing the number of the book on the Libris list (aplhabetically ordered)
        title = A string representing the title of the book
        name_author = A string representing the name of the author
        gender_author = An integer representing a code for the gender of the author (1 = male, 2 = female)
        age_author = An integer representing a code for the age of the author (1 = <25, 2 = 26-35, 3 = 36-45, 4= 46-55, 5 = 56-64, 6 = 65+)
        publisher = A string representing the name of the publisher 
        perspective = An integer representing a code for the narrative situtation in the novel (1 = 1stpers, 2 = 3rdpers, 3 = multi, 4 = other)
        filename =  A string representing the name of the plain text file of the novel, ending with '_clean.txt'
        word_count = An integer representing the number of words the book has
    """

    def __init__(self, book_id, title, name_author, gender_author, age_author, publisher, perspective, filename):
        self.allcharacters = {}
        self.originaltext = ""
        self.markedtext = ""
        self.markedtext_char = ""
        self.markedtext_words = []
        self.markedtext_sentences = []
        self.book_id = book_id
        self.title = title
        self.name_author = name_author
        self.gender_author = gender_author
        self.age_author = age_author
        self.publisher = publisher
        self.perspective = perspective
        self.filename = filename
        self.word_count = 0
        self.name_counts = {}
        self.network = Network(book_id, self.word_count, self.gender_author, self.age_author) # Every time a book object is created, a Network object is also created
    



    def addcharacter(self, book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession):
        """ Adds instances of Character to instances of Book

        """
        
        self.allcharacters[character_id] = Character(book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession)

        if self.perspective == 1:
            self.allcharacters['1'].isfirstperson=True 
        


    def readfile(self, path):
        """ Reads files from instances of Book

        """
        try:
            with open(path+'/'+self.filename, 'rt') as f:
                self.originaltext = f.readlines()
                self.originaltext = "".join(self.originaltext)
                #self.markedtext = "".join(self.originaltext)
                self.markedtext = self.originaltext
        except IOError as exc:
            print ("SOMETHING GOES WRONG IN READING THE FILE of book_id:", self.book_id)
            if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
                raise # Propagate other kinds of IOError.


    

    def replace_namevariants(self):
        """ For the files in every Book object: 
        replace elements in column name_variant in csv-file NAMES_complete with the following marker

        'book_id_character_id_name_namevariant'

        """    

        for character_id in self.allcharacters:
            character = self.allcharacters[character_id]
            #print(character.namevariants)
            for namevariant in sorted(character.namevariants,key=len,reverse=True): # Start with the longest namevariant per character
                marked_name = list(character.name) 
                marked_name = '|'.join(marked_name) # Alter each name so that names won't be overwritten multiple times
                marked_namevariant = list(namevariant) 
                marked_namevariant ='|'.join(marked_namevariant) # Alter each namevariant so that namevariant won't be overwritten multiple times
                

                self.markedtext = self.markedtext.replace(namevariant, self.book_id+'_'+character.character_id+'_'+marked_name.replace(' ','+++')+'_'+marked_namevariant.replace(' ','+++'))


    




    def novel_word_count(self):
        """Computes the total word count of the text file

        """

        self.word_count = sum(len(line.split()) for line in self.originaltext)
        self.network.word_count = self.word_count

        



    def chapter_word_count(self,indices):
        """ Function for computing the word count of specific chapters

        E.g. aaron_chapters, sigerius_chapters or first_chapter, last_chapter, all_chapters

        Relevant for novels in NOVEL_multi

        """
        return sum(len(line.split()) for ch_start, ch_end in indices for line in self[ch_start: ch_end].readfile(path)) 


    # first_chapter = [(34, 81)]
    # all_chapters = [(0, 6813)]
    # print (chapter_word_count(all_chapters, open_files(NOVELS_1stpers)))




    def split_multinovel(self):
        """ Function to split multi-novels (perspective 3) in separate subbooks

        """

        subbooks = []
        subbooknr = 0

        booktext = re.sub(r"\n","<NL>",self.originaltext) # Replace newlines with something else in order for the pattern matching to work
        patterns = re.findall(r"\[START_(\d+)_(\d+)_([^\]]+)\](((?!\[END).)*)\[END_(\d+)_(\d+)_([^\]]+)\]",booktext)


        if patterns:
            for pat in patterns:
                subbooknr += 1
                startbookid = pat[0]
                startcharacterid = pat[1]
                startperspective = pat[2]
                text = re.sub("<NL>","\n",pat[3])
                endbookid = pat[5]
                endcharacterid = pat[6]
                endperspective = pat[7]

                if not startbookid == endbookid:
                    print ('book_id causing ERROR =,', self.book_id, '### startbookid does not equal endbookid ###,', 'startbookid =', startbookid, 'endbookid =', endbookid)
                    exit(0)
                if not startcharacterid == endcharacterid:
                    print ('book_id causing ERROR =', self.book_id,'### startcharacterid does not equal endcharacterid ###,', 'startcharacterid =', startcharacterid, 'endcharacterid =', endcharacterid)
                    exit(0)
                if not startperspective == endperspective:
                    print ('book_id causing ERROR =', self.book_id,'### startperspective does not equal endperspective ###,', 'startperspective =', startperspective, 'endperspective =', endperspective)
                    exit(0)

                book_id = self.book_id + '+' + str(subbooknr) # Create specific book_id for subbook

                if startperspective == 'pers3':
                    perspective = '2'
                else:
                    perspective = '1'

                subbook = Book(self.book_id, self.title, self.name_author, self.gender_author, self.age_author, self.publisher, perspective, 'subbook')
                subbook.originaltext = text
                subbook.markedtext = text
                subbook.novel_word_count()
                            


                for character_id in self.allcharacters:
                    #subbook.addcharacter(self.allcharacters[character].book_id, self.allcharacters[character].character_id, self.allcharacters[character].name, self.allcharacters[character].gender, self.allcharacters[character].descent_country, self.allcharacters[character].descent_city, self.allcharacters[character].living_country, self.allcharacters[character].living_city, self.allcharacters[character].age, self.allcharacters[character].education, self.allcharacters[character].profession)
                    subbook.allcharacters[character_id] = self.allcharacters[character_id]
                    

                    if subbook.allcharacters[character_id].name == startperspective: # Multi-novels are annotated as bookid_characterid_namefirstperson when the subbook is 1stpers
                        subbook.allcharacters[character_id].isfirstperson = True
                        firstcharacterfound = True
                        #print ('CHARACTER = 1stpers')
                    else:
                        subbook.allcharacters[character_id].isfirstperson = False

                if perspective == 1 and not firstcharacterfound:
                    print('book_id causing ERROR =', self.book_id,"ERROR: first person character not found")
                    exit(0)


                #subbook.replace_namevariants() 


                subbooks.append(subbook) # Append eash subbook Book object to a list        


        return (subbooks)







    def count_names(self):
        """Computes occurrenes of namecode of every Character object in Book object


        """

        for character_id in self.allcharacters: 
            namecode = self.allcharacters[character_id].namecode
            count = self.markedtext.count(namecode) 
            #print (namecode, count) 
            self.name_counts[character_id] = count
        #print (self.name_counts)





    def tokenize_text(self):
        """ Tokenizes self.markedtext using the Ucto library from LaMachine. 

        Output:
            self.markedtext_sentences: a list of strings, each string represents a sentence



        """

        

        configurationfile = "tokconfig-nld" 
        tokenizer = ucto.Tokenizer(configurationfile)
        tokenizer.process(self.markedtext)


        # Print number of words of the text
        # nr_of_tokens = 0
        # for token in tokenizer:
        #     nr_of_tokens += 1
        # print ('Number of tokens of book', self.book_id, '=', nr_of_tokens)



        # Print all tokens in the text
        # for token in tokenizer:
        #     print(str(token))
        #     if token.isendofsentence():
        #         print()
        #     elif not token.nospace():
        #         print(" ",end="") 



        for sentence in tokenizer.sentences():
            sentence = re.sub('\s*\|\s*','|',sentence)
            self.markedtext_sentences.append(sentence)
            #print(sentence)
        # for sentence in self.markedtext_sentences:
        #     print (sentence)

    


    def sliding_window_co_occurrence (self, characternr1, characternr2, windowsize=2):
        """ Computes counts of co_occurences of names in sliding window 
        --> weight relations between all characters (without I-narrator)

        Parameters are:
            markedtext_char: window-units of character
            markedtext_word: window-units of words
            markedtext_sentences: window-units of sentences


        """
       

        character1 = self.allcharacters[str(characternr1)]
        character2 = self.allcharacters[str(characternr2)]


        co_occurrence_count = 0

        skipthis = False

        self.markedtext_char = "".join(self.markedtext) # Splits markedtext into a string of characters
        self.markedtext_words = self.markedtext.split() # Splits markedtext into a list of words
        # Or use: self.markedtext_sentences 
      

        for startnr in range(0,len(self.markedtext_sentences)-windowsize):
            if not skipthis:
                secondfound = -1
                character1pos = -1
                character2pos = -1
                for startnr2 in range(startnr, startnr+windowsize):
                    # print(character1.namecode)
                    # print(character2.namecode)
                    # print(self.markedtext_sentences[startnr2])
                    if self.markedtext_sentences[startnr2].find(character1.namecode) > -1:
                        #print("Found!")
                        character1pos = startnr2
                    if self.markedtext_sentences[startnr2].find(character2.namecode) > -1:
                        #print("Found!")
                        character2pos = startnr2

                # searchtext = self.markedtext_sentences[startnr:startnr+windowsize]
                # character1pos = searchtext.find(character1.namecode)
                # character2pos = searchtext.find(character2.namecode)


                if character1pos > -1 and character2pos > -1:
                    co_occurrence_count += 1
                    secondfound = max(character1pos,character2pos)
                    skipthis = True
                    # print(startnr, windowsize)
                    # print('===')
                    # print (" ".join(self.markedtext_sentences[startnr:startnr+windowsize]))
                    # print('=============================')

            else:
                secondfound -= 1
                if secondfound < 0:
                    skipthis = False

        return (co_occurrence_count)



    # print ('The cooccurrence of name character1 and name character2 in the novel is:', sliding_window_co_occurrence(text, 'Nathan', 'Kareltje', windowsize=1000))







    def compute_network(self, filename='social_balance_characters.csv'):
        """    Function for computing the weight of character relations

        Book objects are sorted on the basis of perspective (1, 2, 3). 
        For each perspective another method for computing the weight is used.

        """

        #print ('all characters of book', self.book_id, '=',self.allcharacters)
            

        if self.perspective == '1' or self.perspective == '2':
            """ In case the attribute 'perspective' of Book object equals 1 (1stpers) or 2 (3rdpers) do this ...

            """

            self.replace_namevariants() # Replace names in the text with namecodes
            self.tokenize_text() # Transform the text into a list of sentences
            self.count_names() # Call count_names to compute all occurences of namecodes per Character object

            nrofcharacters = len(self.allcharacters)

            for characternr1 in range(1,nrofcharacters+1): # Start at character_id 1, end at nrocharacters+1 in order to keep the range going for the second for loop
                characternr1str = str(characternr1) # Transform the integer into a string
                #print("char1str = "+characternr1str)
                for characternr2 in range(characternr1+1,nrofcharacters+1): # Start at characternr+1 to skip self loops
                    characternr2str = str(characternr2) # Transform the integer into a string
                    #print("char2str = "+characternr2str)
                    if self.allcharacters[characternr1str].isfirstperson:
                        weight = self.name_counts[characternr2str]  # Weight is the occurences of a character (namecode) in the text
                        #print ('count_names weight', characternr1str, characternr2str, weight)
                        if weight > 0:
                            self.network.add_weight(characternr1str, characternr2str, weight) # Add the weights of firstpersonnarrator ['1'] with all the character to Network object in Book object
                            #self.network.normalize_weights(characternr1str, characternr2str, weight, self.word_count)

                    elif self.allcharacters[characternr2str].isfirstperson:
                        weight = self.name_counts[characternr1str]  # Weight is the occurences of a character (namecode) in the text
                        #print ('count_names weight', characternr2str, characternr1str, weight)
                        if weight > 0:
                            self.network.add_weight(characternr2str, characternr1str, weight) # Add the weights of firstpersonnarrator ['1'] with all the character to Network object in Book object
                            #self.network.normalize_weights(characternr1str, characternr2str, weight, self.word_count)
                            
                    else:
                        weight = self.sliding_window_co_occurrence(characternr1str, characternr2str) # Count weight relation characters with other characters
                        #print ('sliding_window weight', characternr1str, characternr2str, weight)
                        if weight > 0:
                            self.network.add_weight(characternr1str, characternr2str, weight) # Add the weights of all the characters to Network object in Book object
                            #self.network.normalize_weights(characternr1str, characternr2str, weight, self.word_count)
                            self.network.add_weight(characternr2str, characternr1str, weight) # Add the weights of all the characters to Network object in Book object
                            #self.network.normalize_weights(characternr2str, characternr1str, weight, self.word_count)
                        
            self.network.normalize_weights(self.word_count) # Normalize weights by dividing through word_count 
            self.network.networkx_ranking(self.allcharacters) # Rank all characters in Book objects with networkx
            self.network.compute_socialbalance(self.allcharacters, filename='social_balance_characters.csv')


        elif self.perspective == '3': 
            """ In case the attribute 'perspective' of Book object equals 3 (multi) do this ...

            

            """


            
            subbooks = self.split_multinovel() # Split Book object in list of subbooks based on separate character perspectives
        

            for subbook in subbooks:
                """ Parameters:

                1: firstperson approach
                2: 3rdperson approach

                """
                subbook.compute_network() # Call compute_network() to compute the weights for each subbook according to its narrative mode

                self.network.compose_network(subbook) # Compose network of separate subbooks by summing all the separate weights to self.composed(weights)
                self.word_count += subbook.word_count # Add all the separate subbook.word_count to the 'mother' Book self.word_count
            #     print ('subbook word_count = ',subbook.word_count)
            #     print ('**************************************')

            # print ('mother book word_count =', self.word_count)


            self.network.normalize_weights(self.word_count) # Normalize weights for 'mother' Book-object
            self.network.networkx_ranking(self.allcharacters) # Rank all characters in 'mother' Book-object with networkx
            self.network.compute_socialbalance(self.allcharacters, filename='social_balance_characters.csv') 



        else:
            print ('Something goes wrong! Book object is not in one of the three perspective-categories!')
            print ('Book object causing the error:', self.book_id, self.title) # Print instance to which the error is due
            exit(1)


  

    def write_to_csv(self,filename='character-rankings.csv'):
        """
        Function to pass Character information to write_to_csv function in class Network

        """
        self.network.write_to_csv(filename)


         



class Network(): 

    """ A network with the following properties:

    Attributes: 
        book_id = An integer representing the number of the book on the Libris list (aplhabetically ordered)
        word_count = An integer representing the number of words per Book object
        gender_author = An integer representing a code for the gender of the author (1 = male, 2 = female)
        age_author = An integer representing a code for the age of the author (1 = <25, 2 = 26-35, 3 = 36-45, 4= 46-55, 5 = 56-64, 6 = 65+)
        
    """


    
    def __init__(self, book_id, word_count, gender_author, age_author):
        self.weights = {}
        self.relation_type = {}
        self.normalized_weights = {}
        #self.composed_weights = Counter()
        self.Graph = nx.Graph() # networkx Graph object
        self.book_id = book_id
        self.word_count = word_count
        self.gender_author = gender_author
        self.age_author = age_author
        self.number_of_nodes = 0
        self.number_of_edges = 0
        self.density = 0
        self.triadic_closure = 0
        self.clustering_coefficient = 0
        self.is_connected = False 
        #self.diameter = 0
        self.gender_assortativity = 0
        self.descent_country_assortativity = 0
        self.descent_city_assortativity = 0
        self.living_country_assortativity = 0
        self.living_city_assortativity = 0
        self.age_assortativity = 0
        self.education_assortativity = 0
        self.communities = []
        self.community_a = set()
        self.community_b = set()
        self.gender_distribution_book = {'male': 0, 'female': 0, 'unknown': 0}
        self.descent_recode_distribution_book = {'non-migrant': 0, 'migrant': 0, 'unknown': 0}
        self.education_distribution_book = {'high education': 0, 'low education': 0, 'unknown': 0}
        self.age_distribution_book = {'<25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-64': 0, '65+': 0, 'unknown': 0}
        self.gender_distribution_community_a = {'male': 0, 'female': 0, 'unknown': 0}
        self.descent_recode_distribution_community_a = {'non-migrant': 0, 'migrant': 0, 'unknown': 0}
        self.education_distribution_community_a = {'high education': 0, 'low education': 0, 'unknown': 0}
        self.age_distribution_community_a = {'<25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-64': 0, '65+': 0, 'unknown': 0}
        self.gender_distribution_community_b = {'male': 0, 'female': 0, 'unknown': 0}
        self.descent_recode_distribution_community_b = {'non-migrant': 0, 'migrant': 0, 'unknown': 0}
        self.education_distribution_community_b = {'high education': 0, 'low education': 0, 'unknown': 0}
        self.age_distribution_community_b = {'<25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-64': 0, '65+': 0, 'unknown': 0}

        self.balancedtriads1 = 0
        self.balancedtriads2 = 0
        self.forbiddentriads1 = 0
        self.forbiddentriads2 = 0

        self.triad_class = {}



        
    def add_edge(self,source, target, relation_type):
        """ Function for adding eges in every Book object 

        Arguments:
            source: An integer representing a charracter_id
            target: An integer representing a charracter_id
            relation_type: A string representing a type of relation between two characters (lover, friend, enemy, colleage, family (with subclasses))


        """
        if not source in self.relation_type: # If source is not already in self.relation_type ...
            self.relation_type[source] = {} # Create empty dictionary by defining the source as key in self.relation_type
        self.relation_type[source][target] = relation_type # Define relation_type in EDGES-csv as dictionary with source as key and target as value
        
        # for source1 in self.relation_type:
        #     for target1 in self.relation_type[source1]:
        #         #pass
        #          print(source1,target1, self.relation_type[source1][target1])
        # print('============================')


    def add_weight(self, source, target, weight):
        """ Function for adding weight between Character objects in every Book object 

         Arguments:
            source: An integer representing a charracter_id
            target: An integer representing a charracter_id
            relation_type: A string representing a type of relation between two characters (lover, friend, enemy, colleage, family (with subclasses))
            word_count = An integer representing the word count of the file in the Book object


        """
    

        if source in self.relation_type: # In case source has a relation_type
            if not target in self.relation_type[source]: # In case target has no relation_type
                self.add_edge(source,target,'geen') # Add 'geen' as relation_type between source and target
        else:
            self.relation_type[source] = {} # Otherwise, create a dictionary for source which does NOT have a relation_type
            self.add_edge(source,target,'geen') # And add 'geen' between source and target 

        if not source in self.weights: # If a character is not listed as having an edge in EDGES_complete, than still add weight between character and other characters
            self.weights[source] = {}
        if not target in self.weights[source]:
            self.weights[source][target] = 0
        self.weights[source][target] += weight


        # Block of code to print the weights to check if everything works
        # for source1 in self.weights:
        #     for target1 in self.weights[source1]:
        #         #pass
        #         print(source1,target1) 
        #         if target1 in self.weights[source1]:
        #             #pass
        #             print("%.7f" % self.weights[source1][target1])
        #             print (self.weights[source1][target1])
        #         if target1 in self.relation_type[source1]:
        #             #pass
        #             print(self.relation_type[source1][target1])
        # print('------------------------------')

            


    def compose_network(self, subbook):
        """
        Add weights for each character perspective per subook

        """


        for source in subbook.network.weights: # For every source in the weights dict of each subbook network
            for target in subbook.network.weights[source]: # For every target in the weights dict of each subbook network
                self.add_weight(source, target, subbook.network.weights[source][target]) # Add the weights to self.weights of the 'mother' Book-object [SUM OR ADD?]




    def normalize_weights(self,word_count):
        """
        Normalize weights on the basis of the word count

        """

        for source in self.weights: 
            for target in self.weights[source]:
                if not source in self.normalized_weights:
                    self.normalized_weights[source] = {}    
                self.normalized_weights[source][target] = self.weights[source][target] / word_count # Compute normalized_weights by dividing weights through word_count

        # print (self.book_id, self.weights)
        # print ('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        # print (self.book_id, self.normalized_weights)

        
        # if self.normalized_weights == {}:
        #     print ('self.normalized_weights = empty for book_id:', self.book_id)
        #     exit(0)

   

    
    def networkx_ranking (self, allcharacters):
        """ Function for ranking Character objects within Network object using Python library networkx

        Arguments:
            allcharacters: dictionary containing Character objects

        """


        nodeslist = [] # Create empty list for nodes (networkx needs nodes as a list)
        for character_id in allcharacters:
            nodeslist.append(character_id) # Append all character_id's from allcharacters (=dict) in Book object to the empty list    
            # if character_id in self.normalized_weights:  Only append to nodeslist if character_id is also in normalized_weights
                #nodeslist.append(character_id)     
            #     print (character_id)
            #     print ('====================')
            
    
        # print (nodeslist)
        # print ('//////////////////')


        edgestuplelist = [] # Create empyt list for tuples of edge-pairs + weight
        for source1 in self.normalized_weights: # Or use self.normalized_weights??? 
            for target1 in self.normalized_weights[source1]: # Or use self.normalized_weights??? 
                edgestuple = (source1, target1, self.normalized_weights[source1][target1])    # Convert to tuple / # Or use self.normalized_weights??? 
                edgestuplelist.append(edgestuple)
            
        
        self.Graph.add_nodes_from(nodeslist)
        self.Graph.add_weighted_edges_from(edgestuplelist) # Tuple of list containing node pairs + float weights

        
        # Create empty dictionaries for node attributes
        name_dict = {} 
        gender_dict = {}
        descent_country_dict = {}
        descent_city_dict = {}
        living_country_dict = {}
        living_city_dict = {}
        age_dict = {}
        education_dict = {}
        profession_dict = {}
        degree_dict = {}
        betweenness_dict = {}
        closeness_dict = {}
        eigenvector_dict = {}
        katz_dict = {}
        descent_recode_dict = {}

        #print ('allcharacters:', allcharacters)

        for character_id in allcharacters:
            """Define node attributes by accessing Character attributes in allcharacters

            """



            name_dict[character_id] = allcharacters[character_id].name
            gender_dict[character_id] = allcharacters[character_id].gender
            descent_country_dict[character_id] = allcharacters[character_id].descent_country
            descent_city_dict[character_id] = allcharacters[character_id].descent_city
            living_country_dict[character_id] = allcharacters[character_id].living_country
            living_city_dict[character_id] = allcharacters[character_id].living_city
            age_dict[character_id] = allcharacters[character_id].age
            education_dict[character_id] = allcharacters[character_id].education
            profession_dict[character_id] = allcharacters[character_id].profession
            degree_dict[character_id] = 0
            betweenness_dict[character_id] = 0
            closeness_dict[character_id] = 0
            eigenvector_dict[character_id] = 0
            katz_dict[character_id] = 0

            if (allcharacters[character_id].descent_country == '1') or (allcharacters[character_id].descent_country == '2'):
                descent_recode_dict[character_id] = '0' # Recode 1 (Dutch) and 2 (Belgian) into 0 ('non-migrant')
            if (allcharacters[character_id].descent_country == '3') or (allcharacters[character_id].descent_country =='4') or (allcharacters[character_id].descent_country =='5') or (allcharacters[character_id].descent_country =='6'):
                descent_recode_dict[character_id] = '1' # Recode 3 (European), 4 (Western), 5 (Middle Eastern), 6 (Other) into 1 ('migrant')
            if allcharacters[character_id].descent_country == '99':
                descent_recode_dict[character_id] = '99' # 99 (unknown) remains the same


            allcharacters[character_id].descent_recode = descent_recode_dict[character_id] # Add attribute to Character object
            #print ('book_id:', allcharacters[character_id].book_id, 'char_id:', allcharacters[character_id].character_id, 'descent_recode:', allcharacters[character_id].descent_recode)

            # Check if recoding descent_country into descent_recode worked properly
            # print ('character =', allcharacters[character_id].name, 'descent_country =', allcharacters[character_id].descent_country)
            # print ('character =', allcharacters[character_id].name, 'descent_recode =', descent_recode_dict[character_id])
            # print ('***************************************')
      


        nx.set_node_attributes(self.Graph, name_dict, 'name')
        nx.set_node_attributes(self.Graph, gender_dict, 'gender')
        nx.set_node_attributes(self.Graph, descent_country_dict, 'descent_country')
        nx.set_node_attributes(self.Graph, descent_city_dict, 'descent_city')
        nx.set_node_attributes(self.Graph, living_country_dict, 'living_country')
        nx.set_node_attributes(self.Graph, living_city_dict, 'living_city')
        nx.set_node_attributes(self.Graph, age_dict, 'age')
        nx.set_node_attributes(self.Graph, education_dict, 'education')
        nx.set_node_attributes(self.Graph, profession_dict, 'profession')
        nx.set_node_attributes(self.Graph, degree_dict, 'degree')
        nx.set_node_attributes(self.Graph, betweenness_dict, 'betweenness')
        nx.set_node_attributes(self.Graph, closeness_dict, 'closeness')
        nx.set_node_attributes(self.Graph, eigenvector_dict, 'eigenvector')
        nx.set_node_attributes(self.Graph, katz_dict, 'katz')
        nx.set_node_attributes(self.Graph, descent_recode_dict, 'descent_recode')
        nx.set_node_attributes(self.Graph, self.gender_author, 'gender_author')




        # print(nx.info(self.Graph)) # Print information about the Graph   

        # density = nx.density(self.Graph) # Computes density of the network: he ratio of actual edges in the network to all possible edges in the network (scale 0-1)
        # print("Network density:", density)
 
        # for character_id in self.Graph.nodes(): # Loop through every node
        #     print(character_id, self.Graph.node[character_id]['name']) # Access every node by its name, and then by an attribute

        # Louise_Alexander_path = nx.shortest_path(self.Graph, source='1', target='5')
        # print ('Shortest path between Louise and Alexander:', Louise_Alexander_path)
        # print ('Length of that path:', len(Louise_Alexander_path))
        
        # print(nx.is_connected(self.Graph)) # If your Graph has more than one component, this will return False:

        # components = nx.connected_components(self.Graph) # Next, use nx.connected_components to get the list of components,
        # largest_component = max(components, key=len) # then use the max() command to find the largest one:

        # subgraph = self.Graph.subgraph(largest_component) # Create a "subgraph" of just the largest component
        # diameter = nx.diameter(subgraph) # Then calculate the diameter of the subgraph, just like you did with density.
        # print("Network diameter of largest component:", diameter)

        # triadic_closure = nx.transitivity(self.Graph) # Compute transitivity: how interconnected a graph is in terms of a ratio of actual over possible connections (scale 0-1), all the relationships in your graph that may exist but currently do not
        # print("Triadic closure:", triadic_closure) # 


       

        # 1. DEGREE CENTRALITY
        degree_dict = nx.degree_centrality(self.Graph) # Compute degree centrality of all nodes in the Graph object. IMPORTANT: parameter 'weight' cannot be set, scores are thus unweighted degree
        #degree_dict = self.Graph.degree(self.Graph.nodes(), weight='weight') # Compute degree centrality of all nodes in the Graph object
        nx.set_node_attributes(self.Graph, degree_dict, 'degree') # Put degree as an attribute in the Graph object
        #print (self.Graph.node['1']) # print degree of specific nodes
        #sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True) # Sort dictionary of degrees

        #print ('book_id =', self.book_id, 'Nodes by degree:')
        #for degree in sorted_degree:
        #    print (degree)
        #print ('===============')


        # 2. BETWEENESS CENTRALITY
        betweenness_dict = nx.betweenness_centrality(self.Graph, weight='weight') # Run betweenness centrality
        nx.set_node_attributes(self.Graph, betweenness_dict, 'betweenness') # Put betweenness as an attribute in the Graph object
        #sorted_betweenness = sorted(betweenness_dict.items(), key=itemgetter(1), reverse=True)
        

        #print('book_id =', self.book_id,"Nodes by betweenness:")
        #for betweenness in sorted_betweenness:
        #    print(betweenness)
        #print ('===============')

        # 3. CLOSENESS CENTRALITY
        closeness_dict = nx.closeness_centrality(self.Graph, distance='weight') # Run betweenness centrality
        nx.set_node_attributes(self.Graph, closeness_dict, 'closeness') # Put betweenness as an attribute in the Graph object
        #sorted_closeness = sorted(closeness_dict.items(), key=itemgetter(1), reverse=True)
        

        #print('book_id =', self.book_id,"Nodes by closeness:")
        #for closeness in sorted_closeness:
        #    print(closeness)
        #print ('===============')


        # 4. EIGENVECTOR CENTRALITY
        eigenvector_dict = nx.eigenvector_centrality_numpy(self.Graph, weight='weight') # Run eigenvector centrality
        nx.set_node_attributes(self.Graph, eigenvector_dict, 'eigenvector') # Put eigenvector as an attribute in the Graph object
        #sorted_eigenvector = sorted(eigenvector_dict.items(), key=itemgetter(1), reverse=True)

        #print('book_id =', self.book_id,"Nodes by eigenvector:")
        #for eigenvector in sorted_eigenvector:
        #    print(eigenvector)
        #print ('===============')

        # 5. KATZ CENTRALITY
        katz_dict = nx.katz_centrality(self.Graph, weight='weight') # Run eigenvector centrality
        nx.set_node_attributes(self.Graph, katz_dict, 'katz') # Put eigenvector as an attribute in the Graph object
        #sorted_katz = sorted(katz_dict.items(), key=itemgetter(1), reverse=True)

        #print('book_id =', self.book_id,"Nodes by katz:")
        #for katz in sorted_katz:
        #    print(katz)
        #print ('===============')


        # 6. ADD CENTRALITY VALUES TO CHARACTER OBJECTS

        for character_id in allcharacters:
            allcharacters[character_id].degree += degree_dict[character_id]
            #print (allcharacters[character_id].degree)
            allcharacters[character_id].betweenness += betweenness_dict[character_id]
            #print (allcharacters[character_id].betweenness)
            allcharacters[character_id].closeness += closeness_dict[character_id]
            #print (allcharacters[character_id].closeness)
            allcharacters[character_id].eigenvector += eigenvector_dict[character_id]
            #print (allcharacters[character_id].eigenvector)
            allcharacters[character_id].katz += katz_dict[character_id]
            #print (allcharacters[character_id].katz)










    def compute_socialbalance(self, allcharacters, filename='social_balance_characters.csv'):
        """
        Compute social balance for each triad of Character objects in each Book object

        balanced1: +++
        balanced2: 00+
        forbidden1: 000
        forbidden2: ++0

        self.weights variable is dict with character_ids as keys and a nested dict as values, where nested dict key-value pair is target character_id and weight of relation source-target
        allcharacters variable is dict with character_ids as keys and characterobjects as value

        For each possible combination of three Character object in allcharacters, check whether or not these three Character objects have or do not share edges.

        Count the amount of occurrences of a Character object for each of these categories, where + represents an edge and 0 represents NO edge.

        balanced1: +++  ---> triad class key '3'
        balanced2: 00+  ---> triad class key '1'
        forbidden1: 000 ---> triad class key '0'
        forbidden2: ++0 ---> triad class key '2'

        self.balancedtriads1 = 0
        self.balancedtriads2 = 0
        self.forbiddentriads1 = 0
        self.forbiddentriads2 = 0


        """

        # co_occurrences = {} # dict to track whether or not two character in allcharacters share an edge
    

        # for character_id in allcharacters: # Loop over each Character object in dict, key = character_id and value = character object
        #     if not character_id in co_occurrences:
        #         co_occurrences[character_id] = [] 

        # for character_id in self.weights:
        #     co_occurring_chars = self.weights[character_id].keys() # Maybe do list(self.weights[character_id].keys()) if the output object of key() causes harm
        #     #print ('cooccurring characters of character_id', character_id, co_occurring_chars)
        #     co_occurrences[character_id].append(co_occurring_chars)


        # for allcharacters[character_id].character_id in co_occurrences:
        #     for co_occuring_char in co_occurrences[allcharacters[character_id].character_id]


        # triad_combinations = list(itertools.combinations(allcharacters, 3))

        #print (co_occurrences)



        #print(len(list(itertools.combinations(self.Graph.nodes, 3))))

       
        for nodes in itertools.combinations(self.Graph.nodes, 3):
            n_edges = self.Graph.subgraph(nodes).number_of_edges()
            self.triad_class.setdefault(n_edges, []).append(nodes)

        # For every Character object, check in which of the classes it exists (keys 0, 1, 2 or 3 corresponding to one of the 4 (im)balance categories) and increment the corresponding balance attribute with one

        # for key in triad_class:
        #     print ('key:', key, type(key), 'items in list:', len(triad_class[key]))

        # To do: add if-loop that only works if key in dict has values!

        if 3 in self.triad_class:
            #print ('key 3 exists for', self.book_id)
            self.balancedtriads1 += len(self.triad_class[3])

        if 1 in self.triad_class:
            #print ('key 1 exists for', self.book_id)
            self.balancedtriads2 += len(self.triad_class[1])

        if 0 in self.triad_class:
            #print ('key 0 exists for', self.book_id)
            self.forbiddentriads1 += len(self.triad_class[0])

        if 2 in self.triad_class:
            #print ('key 2 exists for', self.book_id)
            self.forbiddentriads2 += len(self.triad_class[2])

        
        self.write_to_csv_social_balance_characters(allcharacters, filename='social_balance_characters.csv')

 
       

    def write_to_csv(self, filename='character-rankings.csv'):
        """
        Writes to columns in new file, for each character in the corpus:

        - book_id
        - character_Id
        - name
        - gender
        - descent_country
        - descent_city
        - living_country
        - living_city
        - age
        - education
        - profession
        - degree_centrality
        - betweenness_centrality
        - closeness_centrality
        - eigenvector
        - katz

        """
        balbla = False
        with open (filename, 'a', newline='') as f:
            csvwriter = csv.writer(f)

            for character_id in sorted(list(self.Graph.nodes)):
                csvwriter.writerow([self.book_id, \
                            character_id, \
                            nx.get_node_attributes(self.Graph, 'name')[character_id], \
                            nx.get_node_attributes(self.Graph, 'gender')[character_id], \
                            nx.get_node_attributes(self.Graph, 'descent_country')[character_id], \
                            nx.get_node_attributes(self.Graph, 'descent_city')[character_id], \
                            nx.get_node_attributes(self.Graph, 'living_country')[character_id], \
                            nx.get_node_attributes(self.Graph, 'living_city')[character_id], \
                            nx.get_node_attributes(self.Graph, 'age')[character_id], \
                            nx.get_node_attributes(self.Graph, 'education')[character_id], \
                            nx.get_node_attributes(self.Graph, 'profession')[character_id], \
                            nx.get_node_attributes(self.Graph, 'degree')[character_id], \
                            nx.get_node_attributes(self.Graph, 'betweenness')[character_id], \
                            nx.get_node_attributes(self.Graph, 'closeness')[character_id], \
                            nx.get_node_attributes(self.Graph, 'eigenvector')[character_id], \
                            nx.get_node_attributes(self.Graph, 'katz')[character_id], \
                            nx.get_node_attributes(self.Graph, 'gender_author')[character_id], \
                            'corpus_Libris2013']
                            )

   



    def write_to_csv_social_balance(self, filename='social_balance.csv'):
        """
        Writes to columns in new file, for each Networkobject, amount of triads in the following categories:

        balanced1: +++
        balanced2: 00+
        forbidden1: 000
        forbidden2: ++0




        """
        blabla = False

        with open (filename, 'a', newline='') as f:
            csvwriter = csv.writer(f)

            csvwriter.writerow([self.book_id, self.balancedtriads1, self.balancedtriads2, self.forbiddentriads1, self.forbiddentriads2])


    def write_to_csv_social_balance_characters(self, allcharacters, filename='social_balance_characters.csv'):
        """
        Writes to rows in csv-file, for each Character object, the following info:

        - book_id
        - character_id
        - demographic data--> gender, descent, education, age

        - in which of the following triad categories it occurs

        balanced1: +++
        balanced2: 00+
        forbidden1: 000
        forbidden2: ++0

        - and if it occurs in one of these triad categories, then for each of these catogories:
            - alter1_character_id
            - alter1_gender
            - alter1_descent
            - alter1_education
            - alter1_age
            - alter1_relation [family, lover, colleague, enemy, friend]
            - alter2_character_id
            - alter2_gender
            - alter2_descent
            - alter2_education
            - alter2_age
            - alter2_relation [family, lover, colleague, enemy, friend]

        """


        # Create list of tuples containing the triad combinations


        try:
            balanced1_triads_list = self.triad_class[3] # balanced1 = category 3
            balanced2_triads_list = self.triad_class[1] # balanced2 = category 1
            forbidden1_triads_list = self.triad_class[0] # forbidden1 = category 0
            forbidden2_triads_list = self.triad_class[2] # forbidden2 = category 2

            # print ('bal1:', balanced1_triads_list)
            # print ('*****************************')
            # print ('bal2:', balanced2_triads_list)
            # print ('*****************************')
            # print ('for1:', forbidden1_triads_list)
            # print ('*****************************')
            # print ('for2:', forbidden2_triads_list)
            # print ('*****************************')


        except KeyError:
            print ('book_id', self.book_id, 'misses one of the triad categories')

        


        with open (filename, 'a', newline='') as f:
            #csvwriter = csv.writer(f)


            fieldnames = ['book_id', 'character_id', 'name', 'gender', 'education', 'age', 'descent_recode', 'triad_cat', \
            'alter1_char_id', 'alter1_name', 'alter1_gender', 'alter1_education', 'alter1_age', 'alter1_descent',  \
            'alter2_char_id', 'alter2_name', 'alter2_gender', 'alter2_education', 'alter2_age', 'alter2_descent']
            csvwriter = csv.DictWriter(f, fieldnames=fieldnames)


            first_dict = {}
            second_dict = {}
            third_dict = {}
            fourth_dict = {}

            for character_id in allcharacters: # Loop over Character objects

            # LOOP OVER BALANCED 1 TRIADS

                try:
                    for triad in balanced1_triads_list:  # Loop over triads (for each of the four lists with triad categories
                        if character_id in triad:
                            #print ('character_id:', character_id, 'in triad:', triad )
                            # print ('character_id:', character_id, 'equals', allcharacters[character_id].character_id)



                            if allcharacters[character_id].character_id == triad[0]: # Access the first node in the triad to store info in a dict
                                #print ('the first item in this triad is character_id:', allcharacters[character_id].character_id)

                                alter1 = triad[1]
                                alter2 = triad[2]


                                first_dict['book_id'] = allcharacters[character_id].book_id
                                first_dict['character_id'] = allcharacters[character_id].character_id
                                first_dict['name'] = allcharacters[character_id].name
                                first_dict['gender'] = allcharacters[character_id].gender
                                first_dict['education'] = allcharacters[character_id].education
                                first_dict['age'] = allcharacters[character_id].age
                                first_dict['descent_recode'] = allcharacters[character_id].descent_recode
                                first_dict['triad_cat'] = 'balanced1'

                                first_dict['alter1_char_id'] = allcharacters[alter1].character_id
                                first_dict['alter1_name'] = allcharacters[alter1].name
                                first_dict['alter1_gender'] = allcharacters[alter1].gender
                                first_dict['alter1_education'] = allcharacters[alter1].education
                                first_dict['alter1_age'] = allcharacters[alter1].age
                                first_dict['alter1_descent'] = allcharacters[alter1].descent_recode

                                first_dict['alter2_char_id'] = allcharacters[alter2].character_id
                                first_dict['alter2_name'] = allcharacters[alter2].name
                                first_dict['alter2_gender'] = allcharacters[alter2].gender
                                first_dict['alter2_education'] = allcharacters[alter2].education
                                first_dict['alter2_age'] = allcharacters[alter2].age
                                first_dict['alter2_descent'] = allcharacters[alter2].descent_recode

                                csvwriter.writerow(first_dict)

                except UnboundLocalError:
                    print ('UnboundLocalError')



            # LOOP OVER BALANCED 2 TRIADS


                try:
                    for triad in balanced2_triads_list:  # Loop over triads (for each of the four lists with triad categories)
                        if character_id in triad:
                            #print ('character_id:', character_id, 'in triad:', triad )
                            # print ('character_id:', character_id, 'equals', allcharacters[character_id].character_id)



                            if allcharacters[character_id].character_id == triad[0]: # Access the first node in the triad to store info in a dict
                                #print ('the first item in this triad is character_id:', allcharacters[character_id].character_id)

                                alter1 = triad[1]
                                alter2 = triad[2]


                                second_dict['book_id'] = allcharacters[character_id].book_id
                                second_dict['character_id'] = allcharacters[character_id].character_id
                                second_dict['name'] = allcharacters[character_id].name
                                second_dict['gender'] = allcharacters[character_id].gender
                                second_dict['education'] = allcharacters[character_id].education
                                second_dict['age'] = allcharacters[character_id].age
                                second_dict['descent_recode'] = allcharacters[character_id].descent_recode
                                second_dict['triad_cat'] = 'balanced2'

                                second_dict['alter1_char_id'] = allcharacters[alter1].character_id
                                second_dict['alter1_name'] = allcharacters[alter1].name
                                second_dict['alter1_gender'] = allcharacters[alter1].gender
                                second_dict['alter1_education'] = allcharacters[alter1].education
                                second_dict['alter1_age'] = allcharacters[alter1].age
                                second_dict['alter1_descent'] = allcharacters[alter1].descent_recode

                                second_dict['alter2_char_id'] = allcharacters[alter2].character_id
                                second_dict['alter2_name'] = allcharacters[alter2].name
                                second_dict['alter2_gender'] = allcharacters[alter2].gender
                                second_dict['alter2_education'] = allcharacters[alter2].education
                                second_dict['alter2_age'] = allcharacters[alter2].age
                                second_dict['alter2_descent'] = allcharacters[alter2].descent_recode

                                csvwriter.writerow(second_dict)

                except UnboundLocalError:
                    print ('UnboundLocalError')


                # LOOP OVER FORBIDDEN 1 TRIADS


                try:
                    for triad in forbidden1_triads_list:  # Loop over triads (for each of the four lists with triad categories)
                        if character_id in triad:
                            #print ('character_id:', character_id, 'in triad:', triad )
                            # print ('character_id:', character_id, 'equals', allcharacters[character_id].character_id)



                            if allcharacters[character_id].character_id == triad[0]: # Access the first node in the triad to store info in a dict
                                #print ('the first item in this triad is character_id:', allcharacters[character_id].character_id)

                                alter1 = triad[1] 
                                alter2 = triad[2]


                                third_dict['book_id'] = allcharacters[character_id].book_id
                                third_dict['character_id'] = allcharacters[character_id].character_id
                                third_dict['name'] = allcharacters[character_id].name
                                third_dict['gender'] = allcharacters[character_id].gender
                                third_dict['education'] = allcharacters[character_id].education
                                third_dict['age'] = allcharacters[character_id].age
                                third_dict['descent_recode'] = allcharacters[character_id].descent_recode
                                third_dict['triad_cat'] = 'forbidden1'

                                third_dict['alter1_char_id'] = allcharacters[alter1].character_id
                                third_dict['alter1_name'] = allcharacters[alter1].name
                                third_dict['alter1_gender'] = allcharacters[alter1].gender
                                third_dict['alter1_education'] = allcharacters[alter1].education
                                third_dict['alter1_age'] = allcharacters[alter1].age
                                third_dict['alter1_descent'] = allcharacters[alter1].descent_recode

                                third_dict['alter2_char_id'] = allcharacters[alter2].character_id
                                third_dict['alter2_name'] = allcharacters[alter2].name
                                third_dict['alter2_gender'] = allcharacters[alter2].gender
                                third_dict['alter2_education'] = allcharacters[alter2].education
                                third_dict['alter2_age'] = allcharacters[alter2].age
                                third_dict['alter2_descent'] = allcharacters[alter2].descent_recode

                                csvwriter.writerow(third_dict)

                except UnboundLocalError:
                    print ('UnboundLocalError')



                # LOOP OVER FORBIDDEN 2 TRIADS

                try:
                    for triad in forbidden2_triads_list:  # Loop over triads (for each of the four lists with triad categories)
                        if character_id in triad:
                            #print ('character_id:', character_id, 'in triad:', triad )
                            # print ('character_id:', character_id, 'equals', allcharacters[character_id].character_id)



                            if allcharacters[character_id].character_id == triad[0]: # Access the first node in the triad to store info in a dict
                                #print ('the first item in this triad is character_id:', allcharacters[character_id].character_id)

                                alter1 = triad[1]# TO WORK ON: DEFINE TRIADS (+ INFO IN RELATED DICTS) IMMEDIATELY AND WRITE INFO ON SOURCE, ALTER1, ALTER2 TO CSV ROW AT ONCE
                                alter2 = triad[2]


                                fourth_dict['book_id'] = allcharacters[character_id].book_id
                                fourth_dict['character_id'] = allcharacters[character_id].character_id
                                fourth_dict['name'] = allcharacters[character_id].name
                                fourth_dict['gender'] = allcharacters[character_id].gender
                                fourth_dict['education'] = allcharacters[character_id].education
                                fourth_dict['age'] = allcharacters[character_id].age
                                fourth_dict['descent_recode'] = allcharacters[character_id].descent_recode
                                fourth_dict['triad_cat'] = 'forbidden2'

                                fourth_dict['alter1_char_id'] = allcharacters[alter1].character_id
                                fourth_dict['alter1_name'] = allcharacters[alter1].name
                                fourth_dict['alter1_gender'] = allcharacters[alter1].gender
                                fourth_dict['alter1_education'] = allcharacters[alter1].education
                                fourth_dict['alter1_age'] = allcharacters[alter1].age
                                fourth_dict['alter1_descent'] = allcharacters[alter1].descent_recode

                                fourth_dict['alter2_char_id'] = allcharacters[alter2].character_id
                                fourth_dict['alter2_name'] = allcharacters[alter2].name
                                fourth_dict['alter2_gender'] = allcharacters[alter2].gender
                                fourth_dict['alter2_education'] = allcharacters[alter2].education
                                fourth_dict['alter2_age'] = allcharacters[alter2].age
                                fourth_dict['alter2_descent'] = allcharacters[alter2].descent_recode

                                csvwriter.writerow(fourth_dict)

                except UnboundLocalError:
                    print ('UnboundLocalError')






                






       



                        # elif allcharacters[character_id].character_id == triad[1]: # Access the second node in the triad to store info on this node in a dict

                        #     #print ('the second item in this triad is character_id:', allcharacters[character_id].character_id)
                        #     alter1 = triad[1]# TO WORK ON: DEFINE TRIADS (+ INFO IN RELATED DICTS) IMMEDIATELY AND WRITE INFO ON SOURCE, ALTER1, ALTER2 TO CSV ROW AT ONCE
                        #     alter2 = triad[2]

                        #     second_dict['book_id'] = allcharacters[character_id].book_id
                        #     second_dict['character_id'] = allcharacters[character_id].character_id
                        #     second_dict['name'] = allcharacters[character_id].name
                        #     second_dict['gender'] = allcharacters[character_id].gender
                        #     second_dict['education'] = allcharacters[character_id].education
                        #     second_dict['age'] = allcharacters[character_id].age
                        #     second_dict['descent_recode'] = allcharacters[character_id].descent_recode
                        #     second_dict['triad_cat'] = 'balanced1'

                        #     second_dict['alter1_char_id'] = allcharacters[alter1].character_id
                        #     second_dict['alter1_name'] = allcharacters[alter1].name
                        #     second_dict['alter1_gender'] = allcharacters[alter1].gender
                        #     second_dict['alter1_education'] = allcharacters[alter1].education
                        #     second_dict['alter1_age'] = allcharacters[alter1].age
                        #     second_dict['alter1_descent'] = allcharacters[alter1].descent_recode

                        #     second_dict['alter2_char_id'] = allcharacters[alter2].character_id
                        #     second_dict['alter2_name'] = allcharacters[alter2].name
                        #     second_dict['alter2_gender'] = allcharacters[alter2].gender
                        #     second_dict['alter2_education'] = allcharacters[alter2].education
                        #     second_dict['alter2_age'] = allcharacters[alter2].age
                        #     second_dict['alter2_descent'] = allcharacters[alter2].descent_recode

                        #     csvwriter.writerow(second_dict)




                        # elif allcharacters[character_id].character_id == triad[2]: # Access the third node in the triad to store info on alter2 in a dict

                        #     #print ('the third item in this triad is character_id:', allcharacters[character_id].character_id)

                        #     alter1 = triad[1]# TO WORK ON: DEFINE TRIADS (+ INFO IN RELATED DICTS) IMMEDIATELY AND WRITE INFO ON SOURCE, ALTER1, ALTER2 TO CSV ROW AT ONCE
                        #     alter2 = triad[2]

                        #     third_dict['book_id'] = allcharacters[character_id].book_id
                        #     third_dict['character_id'] = allcharacters[character_id].character_id
                        #     third_dict['name'] = allcharacters[character_id].name
                        #     third_dict['gender'] = allcharacters[character_id].gender
                        #     third_dict['education'] = allcharacters[character_id].education
                        #     third_dict['age'] = allcharacters[character_id].age
                        #     third_dict['descent_recode'] = allcharacters[character_id].descent_recode
                        #     third_dict['triad_cat'] = 'balanced1'

                        #     third_dict['alter1_char_id'] = allcharacters[alter1].character_id
                        #     third_dict['alter1_name'] = allcharacters[alter1].name
                        #     third_dict['alter1_gender'] = allcharacters[alter1].gender
                        #     third_dict['alter1_education'] = allcharacters[alter1].education
                        #     third_dict['alter1_age'] = allcharacters[alter1].age
                        #     third_dict['alter1_descent'] = allcharacters[alter1].descent_recode

                        #     third_dict['alter2_char_id'] = allcharacters[alter2].character_id
                        #     third_dict['alter2_name'] = allcharacters[alter2].name
                        #     third_dict['alter2_gender'] = allcharacters[alter2].gender
                        #     third_dict['alter2_education'] = allcharacters[alter2].education
                        #     third_dict['alter2_age'] = allcharacters[alter2].age
                        #     third_dict['alter2_descent'] = allcharacters[alter2].descent_recode



    



   









                    # csvwriter.writerow([first_dict['book_id'], \
                    #             first_dict['character_id'], \
                    #             first_dict['name'], \
                    #             first_dict['gender'], \
                    #             first_dict['education'], \
                    #             first_dict['age'], \
                    #             first_dict['descent_recode'], \
                                            
                    #             'balanced1', \

                    #             second_dict['character_id'], \
                    #             second_dict['name'], \
                    #             second_dict['gender'], \
                    #             second_dict['education'], \
                    #             second_dict['age'], \
                    #             second_dict['descent_recode'], \


                    #             third_dict['character_id'], \
                    #             third_dict['name'], \
                    #             third_dict['gender'], \
                    #             third_dict['education'], \
                    #             third_dict['age'], \
                    #             third_dict['descent_recode']])








                        # elif allcharacters[character_id].character_id == triad[1]: # Write demographic info on alter1

                        #     csvwriter.writerow([allcharacters[character_id].character_id, \
                        #         allcharacters[character_id].gender, \
                        #         allcharacters[character_id].education, \
                        #         allcharacters[character_id].age, \
                        #         allcharacters[character_id].descent_recode])   # Write columns: source node demographic info, triad category number, alter1 demographic info, alter2 demopgrahic info

                        # elif allcharacters[character_id].character_id == triad[2]: # Write demographic info on alter2

                        #     csvwriter.writerow([allcharacters[character_id].character_id, \
                        #         allcharacters[character_id].gender, \
                        #         allcharacters[character_id].education, \
                        #         allcharacters[character_id].age, \
                        #         allcharacters[character_id].descent_recode])   # Write columns: source node demographic info, triad category number, alter1 demographic info, alter2 demopgrahic info


                        

 

        # Add node attributes to Network object by accessing the four lists of triad combinations above

        # for character_id in allcharacters: # allcharacters is a dict with character_id's as keys and Character objects as values

        #   balanced1_dict[character_id] = 
        #   balanced2_dict[character_id] = 
        #   forbidden1_dict[character_id] = 
        #   forbidden2_dict[character_id] = 

        
            






        # balbla = False

        # with open (filename, 'a', newline='') as f:
        #     csvwriter = csv.writer(f)

        #     for character_id in sorted(list(self.Graph.nodes)):
        #         csvwriter.writerow([self.book_id, \
        #                     character_id, \
        #                     nx.get_node_attributes(self.Graph, 'name')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'gender')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'descent_country')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'descent_city')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'living_country')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'living_city')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'age')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'education')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'profession')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'degree')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'betweenness')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'closeness')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'eigenvector')[character_id], \
        #                     nx.get_node_attributes(self.Graph, 'katz')[character_id]])
           






    def compute_networkstats(self, filename='networkstats.csv'):
        """
            Computes network statistics for each Network object

                - number of nodes
                - number of edges
                - density 
                - transitivity/triadic closure
                - clustering coefficient
                - diameter
                - assortativity per node attribute

            And writes the results to networkstats.csv 


        """

        self.number_of_nodes = len(self.Graph) # Returns number of nodes
        print ("Number of nodes for book", self.book_id, '=', self.number_of_nodes)

        self.number_of_edges = self.Graph.number_of_edges()  # Returns number of edges
        print ("Number of edges for book", self.book_id, '=', self.number_of_edges)

        self.density = nx.density(self.Graph) # Computes density of the network: the ratio of actual edges in the network to all possible edges in the network (scale 0-1)
        print("Network density for book", self.book_id, '=', self.density)

        self.triadic_closure = nx.transitivity(self.Graph) # Computes transitivity: how interconnected a graph is in terms of a ratio of actual over possible connections (scale 0-1), all the relationships in your graph that may exist but currently do not
        print("Triadic closure for book", self.book_id, '=', self.triadic_closure) 

        self.clustering_coefficient = nx.average_clustering(self.Graph, weight='weight') # Computes the degree to which nodes in a graph tend to cluster together
        print ('The clustering coefficient for book', self.book_id, '=', self.clustering_coefficient)

        self.is_connected = nx.is_connected(self.Graph)
        print ('Is the network of book', self.book_id, 'connected?', self.is_connected)


        # self.diameter = nx.diameter(self.Graph) # Computes the shortest distance between the two most distant nodes in the network which represents the linear size of the network

     

        self.gender_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'gender')
        self.descent_country_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'descent_country')
        self.descent_city_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'descent_city')
        self.living_country_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'living_country')
        self.living_city_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'living_city')
        self.age_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'age')
        self.education_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'education')
        self.descent_recode_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'descent_recode')
        print ('Gender assortativity for book', self.book_id, '=', self.gender_assortativity)
        print ('Country of descent assortativity for book', self.book_id, '=', self.descent_country_assortativity)
        print ('City of descent assortativity for book', self.book_id, '=', self.descent_city_assortativity)
        print ('Country of living assortativity for book', self.book_id, '=', self.living_country_assortativity)
        print ('City of living assortativity for book', self.book_id, '=', self.living_city_assortativity)
        print ('Age assortativity for book', self.book_id, '=', self.age_assortativity)
        print ('Education assortativity for book', self.book_id, '=', self.education_assortativity)
        print ('Descent_recode assortativity for book', self.book_id, '=', self.descent_recode_assortativity)



        with open (filename, 'a', newline='') as f:
            csvwriter = csv.writer(f)

            csvwriter.writerow([self.book_id, \
                        self.word_count, \
                        self.gender_author, \
                        self.age_author, \
                        self.number_of_nodes, \
                        self.number_of_edges, \
                        self.density, \
                        self.triadic_closure, \
                        self.clustering_coefficient, \
                        self.is_connected, \
                        self.gender_assortativity, \
                        self.descent_country_assortativity, \
                        self.descent_city_assortativity, \
                        self.living_country_assortativity, \
                        self.living_city_assortativity, \
                        self.age_assortativity, \
                        self.education_assortativity, \
                        self.descent_recode_assortativity])


    def detect_communities(self, filename='communities_frequency_distributions.csv'):
        """
        Divides the Network object into communities using the Clauset-Newman-Moore modularity maximization, the Girvan-Newman algorithm, the Kernighan–Lin algorithm, or other methods. 

        Greedy modularity maximization begins with each node in its own community and joins the pair of communities that most increases modularity until no such pair exists.

        The Girvan–Newman algorithm detects communities by progressively removing edges from the original graph. The algorithm removes the “most valuable” edge, traditionally the edge with the highest betweenness centrality, at each step. As the graph breaks down into pieces, the tightly knit community structure is exposed and the result can be depicted as a dendrogram.

        The Kernighan–Lin algorithm paritions a network into two sets by iteratively swapping pairs of nodes to reduce the edge cut between the two sets.

        Outputs the results to communities_distributions.csv to use in further statistical analysis


        """

        # communities = list(greedy_modularity_communities(self.Graph))
        # for community in communities:
        #     print ('Communities of book', self.book_id, sorted(community))

        #communities = girvan_newman(self.Graph)
        #print ('Communities of book', self.book_id,tuple(sorted(c) for c in next(communities)))
        #print ('Communities of book', self.book_id,tuple(sorted(communities)))

        # communities = label_propagation_communities(self.Graph)
        # for community in communities:
        #     print ('Communities of book', self.book_id, sorted(community))

        # communities = asyn_lpa_communities(self.Graph)
        # for community in communities:
        #     print ('Communities of book', self.book_id, sorted(community))


        # communities = list(k_clique_communities(self.Graph, 2))
        # for community in communities:
        #     print ('Communities of book', self.book_id, sorted(community))


        self.communities = kernighan_lin_bisection(self.Graph, weight='weight')
        print ('Communities of book', self.book_id, ':', sorted(self.communities))

        self.community_a = self.communities[0]
        self.community_b = self.communities[1]
        print ('Community a of book', self.book_id, ':', self.community_a)
        print ('Community b of book', self.book_id, ':', self.community_b)

        gender_nx = nx.get_node_attributes(self.Graph, 'gender')
        descent_recode_nx = nx.get_node_attributes(self.Graph, 'descent_recode')
        education_nx = nx.get_node_attributes(self.Graph, 'education')
        age_nx = nx.get_node_attributes(self.Graph, 'age')

        for community in self.communities:
            for character_id in community:
                """
                    For the book as a whole, store demographic info in four dictionaries (gender, descent, education, age) to compute distributions


                """
                # print ('character_id:', character_id, 'gender:', gender_nx[character_id])
                # print ('character_id:', character_id, 'descent:', descent_recode_nx[character_id])
                # print ('character_id:', character_id, 'education:', education_nx[character_id])
                # print ('character_id:', character_id, 'age:', age_nx[character_id])
                if gender_nx[character_id] == '1':
                    self.gender_distribution_book['male'] += 1
                elif gender_nx[character_id] == '2':
                    self.gender_distribution_book['female'] += 1
                elif gender_nx[character_id] == '99':
                    self.gender_distribution_book['unknown'] += 1

                if descent_recode_nx[character_id] == '0':
                    self.descent_recode_distribution_book['non-migrant'] += 1
                elif descent_recode_nx[character_id] == '1':
                    self.descent_recode_distribution_book['migrant'] += 1
                elif descent_recode_nx[character_id] == '99':
                    self.descent_recode_distribution_book['unknown'] += 1
                
                if education_nx[character_id] == '1':
                    self.education_distribution_book['high education'] += 1
                elif education_nx[character_id] == '2':
                    self.education_distribution_book['low education'] += 1
                elif education_nx[character_id] == '99':
                    self.education_distribution_book['unknown'] += 1

                if age_nx[character_id] == '1':
                    self.age_distribution_book['<25'] += 1
                elif age_nx[character_id] == '2':
                    self.age_distribution_book['26-35'] += 1
                elif age_nx[character_id] == '3':
                    self.age_distribution_book['36-45'] += 1
                elif age_nx[character_id] == '4':
                    self.age_distribution_book['46-55'] += 1
                elif age_nx[character_id] == '5':
                    self.age_distribution_book['56-64'] += 1
                elif age_nx[character_id] == '6':
                    self.age_distribution_book['65+'] += 1
                elif age_nx[character_id] == '99':
                    self.age_distribution_book['unknown'] += 1


        print ('male characters in book', self.book_id, self.gender_distribution_book['male'])
        print ('female characters in book', self.book_id, self.gender_distribution_book['female'])
        print ('unknown gender characters in book', self.book_id, self.gender_distribution_book['unknown'])

        print ('non-migrant characters in book', self.book_id, self.descent_recode_distribution_book['non-migrant'])
        print ('migrant characters in book', self.book_id, self.descent_recode_distribution_book['migrant'])
        print ('unknown descent characters in book', self.book_id, self.descent_recode_distribution_book['unknown'])

        print ('higher educated characters in book', self.book_id, self.education_distribution_book['high education'])
        print ('lower educated characters in book', self.book_id, self.education_distribution_book['low education'])
        print ('unknown education characters in book', self.book_id, self.education_distribution_book['unknown'])

        print ('age <25 characters in book', self.book_id, self.age_distribution_book['<25'])
        print ('age 26-35 characters in book', self.book_id, self.age_distribution_book['26-35'])
        print ('age 36-45 characters in book', self.book_id, self.age_distribution_book['36-45'])
        print ('age 46-55 characters in book', self.book_id, self.age_distribution_book['46-55'])
        print ('age 56-64 characters in book', self.book_id, self.age_distribution_book['56-64'])
        print ('age unknown characters in book', self.book_id, self.age_distribution_book['unknown'])



        for character_id in self.community_a:
            """
                For community_a, store demographic info in four dictionaries (gender, descent, education, age) to compute distribution


            """
            # print ('character_id:', character_id, 'gender:', gender_nx[character_id])
            # print ('character_id:', character_id, 'descent:', descent_recode_nx[character_id])
            # print ('character_id:', character_id, 'education:', education_nx[character_id])
            # print ('character_id:', character_id, 'age:', age_nx[character_id])
            if gender_nx[character_id] == '1':
                self.gender_distribution_community_a['male'] += 1
            elif gender_nx[character_id] == '2':
                self.gender_distribution_community_a['female'] += 1
            elif gender_nx[character_id] == '99':
                self.gender_distribution_community_a['unknown'] += 1

            if descent_recode_nx[character_id] == '0':
                self.descent_recode_distribution_community_a['non-migrant'] += 1
            elif descent_recode_nx[character_id] == '1':
                self.descent_recode_distribution_community_a['migrant'] += 1
            elif descent_recode_nx[character_id] == '99':
                self.descent_recode_distribution_community_a['unknown'] += 1
            
            if education_nx[character_id] == '1':
                self.education_distribution_community_a['high education'] += 1
            elif education_nx[character_id] == '2':
                self.education_distribution_community_a['low education'] += 1
            elif education_nx[character_id] == '99':
                self.education_distribution_community_a['unknown'] += 1

            if age_nx[character_id] == '1':
                self.age_distribution_community_a['<25'] += 1
            elif age_nx[character_id] == '2':
                self.age_distribution_community_a['26-35'] += 1
            elif age_nx[character_id] == '3':
                self.age_distribution_community_a['36-45'] += 1
            elif age_nx[character_id] == '4':
                self.age_distribution_community_a['46-55'] += 1
            elif age_nx[character_id] == '5':
                self.age_distribution_community_a['56-64'] += 1
            elif age_nx[character_id] == '6':
                self.age_distribution_community_a['65+'] += 1
            elif age_nx[character_id] == '99':
                self.age_distribution_community_a['unknown'] += 1


        print ('male characters in community_a of book', self.book_id, self.gender_distribution_community_a['male'])
        print ('female characters in community_a of book', self.book_id, self.gender_distribution_community_a['female'])
        print ('unknown gender characters in community_a of book', self.book_id, self.gender_distribution_community_a['unknown'])

        print ('non-migrant characters in community_a of book', self.book_id, self.descent_recode_distribution_community_a['non-migrant'])
        print ('migrant characters in community_a of book', self.book_id, self.descent_recode_distribution_community_a['migrant'])
        print ('unknown descent characters in community_a of book', self.book_id, self.descent_recode_distribution_community_a['unknown'])

        print ('higher educated characters in community_a of book', self.book_id, self.education_distribution_community_a['high education'])
        print ('lower educated characters in community_a of book', self.book_id, self.education_distribution_community_a['low education'])
        print ('unknown education characters in community_a of book', self.book_id, self.education_distribution_community_a['unknown'])

        print ('age <25 characters in community_a of book', self.book_id, self.age_distribution_community_a['<25'])
        print ('age 26-35 characters in community_a of book', self.book_id, self.age_distribution_community_a['26-35'])
        print ('age 36-45 characters in community_a of book', self.book_id, self.age_distribution_community_a['36-45'])
        print ('age 46-55 characters in community_a of book', self.book_id, self.age_distribution_community_a['46-55'])
        print ('age 56-64 characters in community_a of book', self.book_id, self.age_distribution_community_a['56-64'])
        print ('age unknown characters in community_a of book', self.book_id, self.age_distribution_community_a['unknown'])


        for character_id in self.community_b:
            """
                For community_b, store demographic info in four dictionaries (gender, descent, education, age) to compute distribution


            """
            # print ('character_id:', character_id, 'gender:', gender_nx[character_id])
            # print ('character_id:', character_id, 'descent:', descent_recode_nx[character_id])
            # print ('character_id:', character_id, 'education:', education_nx[character_id])
            # print ('character_id:', character_id, 'age:', age_nx[character_id])

            if gender_nx[character_id] == '1':
                self.gender_distribution_community_b['male'] += 1
            elif gender_nx[character_id] == '2':
                self.gender_distribution_community_b['female'] += 1
            elif gender_nx[character_id] == '99':
                self.gender_distribution_community_b['unknown'] += 1

            if descent_recode_nx[character_id] == '0':
                self.descent_recode_distribution_community_b['non-migrant'] += 1
            elif descent_recode_nx[character_id] == '1':
                self.descent_recode_distribution_community_b['migrant'] += 1
            elif descent_recode_nx[character_id] == '99':
                self.descent_recode_distribution_community_b['unknown'] += 1
            
            if education_nx[character_id] == '1':
                self.education_distribution_community_b['high education'] += 1
            elif education_nx[character_id] == '2':
                self.education_distribution_community_b['low education'] += 1
            elif education_nx[character_id] == '99':
                self.education_distribution_community_b['unknown'] += 1

            if age_nx[character_id] == '1':
                self.age_distribution_community_b['<25'] += 1
            elif age_nx[character_id] == '2':
                self.age_distribution_community_b['26-35'] += 1
            elif age_nx[character_id] == '3':
                self.age_distribution_community_b['36-45'] += 1
            elif age_nx[character_id] == '4':
                self.age_distribution_community_b['46-55'] += 1
            elif age_nx[character_id] == '5':
                self.age_distribution_community_b['56-64'] += 1
            elif age_nx[character_id] == '6':
                self.age_distribution_community_b['65+'] += 1
            elif age_nx[character_id] == '99':
                self.age_distribution_community_b['unknown'] += 1


        print ('male characters in community_b of book', self.book_id, self.gender_distribution_community_b['male'])
        print ('female characters in community_b of book', self.book_id, self.gender_distribution_community_b['female'])
        print ('unknown gender characters in community_b of book', self.book_id, self.gender_distribution_community_b['unknown'])

        print ('non-migrant characters in community_b of book', self.book_id, self.descent_recode_distribution_community_b['non-migrant'])
        print ('migrant characters in community_b of book', self.book_id, self.descent_recode_distribution_community_b['migrant'])
        print ('unknown descent characters in community_b of book', self.book_id, self.descent_recode_distribution_community_b['unknown'])

        print ('higher educated characters in community_b of book', self.book_id, self.education_distribution_community_b['high education'])
        print ('lower educated characters in community_b of book', self.book_id, self.education_distribution_community_b['low education'])
        print ('unknown education characters in community_b of book', self.book_id, self.education_distribution_community_b['unknown'])

        print ('age <25 characters in community_b of book', self.book_id, self.age_distribution_community_b['<25'])
        print ('age 26-35 characters in community_b of book', self.book_id, self.age_distribution_community_b['26-35'])
        print ('age 36-45 characters in community_b of book', self.book_id, self.age_distribution_community_b['36-45'])
        print ('age 46-55 characters in community_b of book', self.book_id, self.age_distribution_community_b['46-55'])
        print ('age 56-64 characters in community_b of book', self.book_id, self.age_distribution_community_b['56-64'])
        print ('age unknown characters in community_b of book', self.book_id, self.age_distribution_community_b['unknown'])


        with open (filename, 'a', newline='') as f:
            csvwriter = csv.writer(f)

            csvwriter.writerow([self.gender_distribution_book['male'], \
                        self.gender_distribution_book['female'], \
                        self.gender_distribution_book['unknown'], \
                        self.gender_distribution_community_a['male'], \
                        self.gender_distribution_community_a['female'], \
                        self.gender_distribution_community_a['unknown'], \
                        self.gender_distribution_community_b['male'], \
                        self.gender_distribution_community_b['female'], \
                        self.gender_distribution_community_b['unknown'], \
                        self.descent_recode_distribution_book['non-migrant'], \
                        self.descent_recode_distribution_book['migrant'], \
                        self.descent_recode_distribution_book['unknown'], \
                        self.descent_recode_distribution_community_a['non-migrant'], \
                        self.descent_recode_distribution_community_a['migrant'], \
                        self.descent_recode_distribution_community_a['unknown'], \
                        self.descent_recode_distribution_community_b['non-migrant'], \
                        self.descent_recode_distribution_community_b['migrant'], \
                        self.descent_recode_distribution_community_b['unknown'], \
                        self.education_distribution_book['high education'], \
                        self.education_distribution_book['low education'], \
                        self.education_distribution_book['unknown'], \
                        self.education_distribution_community_a['high education'], \
                        self.education_distribution_community_a['low education'], \
                        self.education_distribution_community_a['unknown'], \
                        self.education_distribution_community_b['high education'], \
                        self.education_distribution_community_b['low education'], \
                        self.education_distribution_community_b['unknown'], \
                        self.age_distribution_book['<25'], \
                        self.age_distribution_book['26-35'], \
                        self.age_distribution_book['36-45'], \
                        self.age_distribution_book['46-55'], \
                        self.age_distribution_book['56-64'], \
                        self.age_distribution_book['65+'], \
                        self.age_distribution_book['unknown'], \
                        self.age_distribution_community_a['<25'], \
                        self.age_distribution_community_a['26-35'], \
                        self.age_distribution_community_a['36-45'], \
                        self.age_distribution_community_a['46-55'], \
                        self.age_distribution_community_a['56-64'], \
                        self.age_distribution_community_a['65+'], \
                        self.age_distribution_community_a['unknown'], \
                        self.age_distribution_community_b['<25'], \
                        self.age_distribution_community_b['26-35'], \
                        self.age_distribution_community_b['36-45'], \
                        self.age_distribution_community_b['46-55'], \
                        self.age_distribution_community_b['56-64'], \
                        self.age_distribution_community_b['65+'], \
                        self.age_distribution_community_b['unknown']])





            
    def draw_network(self, filename='networkx_graph.gexf'):
        """
        Draws network and show the visualization in a WebAgg server

        """
        nx.draw_networkx(self.Graph, pos=nx.random_layout(self.Graph))
        plt.draw()
        plt.show()

        nx.write_gexf(self.Graph, filename) # Export the data as a GEXF file to upload in Gephi for visualization


































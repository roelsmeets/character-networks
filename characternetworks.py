# #!/usr/bin/env python

# # -*- coding: utf-8 -*-

# 1. IMPORTS

from collections import Counter
import itertools 
import networkx as nx
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

        self.marked_name = list(self.name) 
        self.marked_name = '|'.join(self.marked_name)
        self.namecode = self.book_id+'_'+self.character_id+'_'+self.marked_name.replace(' ','+++') # DOES THIS MATCH THE NAMECODE IN def replace_namvariants?

        



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
        self.network = Network(book_id) # Every time a book object is created, a Network object for each book_id is also created
    



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







    def compute_network(self):
        """    Function for computing the weight of character relations

        Book objects are sorted on the basis of perspective (1, 2, 3). 
        For each perspective another method for computing the weight is used.

        """
            

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
        
    """


    
    def __init__(self, book_id):
        self.weights = {}
        self.relation_type = {}
        self.normalized_weights = {}
        #self.composed_weights = Counter()
        self.Graph = nx.Graph() # networkx Graph object
        self.book_id = book_id

        
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
        # for source1 in self.normalized_weights:
        #     for target1 in self.normalized_weights[source1]:
        #         #pass
        #         print(source1,target1) 
        #         if target1 in self.normalized_weights[source1]:
        #             #pass
        #             print("%.7f" % self.normalized_weights[source1][target1])
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

        #print (self.book_id, self.weights)
        #print ('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        #print (self.book_id, self.normalized_weights)

        
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
                            nx.get_node_attributes(self.Graph, 'katz')[character_id]])





    def compute_assortativity(self):
    	"""
    	Computes assortativity per node attribute for each Book object


    	"""


    	gender_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'gender')
    	descent_country_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'descent_country')
    	descent_city_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'descent_city')
    	living_country_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'living_country')
    	living_city_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'living_city')
    	age_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'age')
    	education_assortativity = nx.attribute_assortativity_coefficient(self.Graph, 'education')

    	print ('gender assortativity for book', self.book_id, '=', gender_assortativity)



    	#nx.write_gexf(self.Graph, 'sample_graph.gexf') # Export the data as a GEXF file to upload in Gephi for visualization


































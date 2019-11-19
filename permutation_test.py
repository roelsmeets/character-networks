# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# 1. IMPORTS

import argparse
from collections import Counter 
from itertools import islice
import networkx as nx
import matplotlib.pyplot as plt
import re
import nltk
import pandas as pd
import numpy as np
import os
import glob
import sys
import errno
import csv
from characternetworks_2 import Book, Character, Network

from variables import *

argparser = argparse.ArgumentParser(description='computes character network of (subset of) novels')
argparser.add_argument('--task', default=1, type=int, help='number of task when parallelising')
argparser.add_argument('--total', default=1, type=int, help='total number of tasks when parallelising')
args = argparser.parse_args()
parameters=vars(args)
task = parameters['task']
total = parameters['total']
if task > total:
    sys.exit('task can not be higher than total!')
    

# 2. INPUT

with open(csvfiles['books'], 'rt') as csvfile1, \
     open(csvfiles['nodes'], 'rt') as csvfile2, \
     open(csvfiles['edges'], 'rt') as csvfile3, \
     open(csvfiles['names'], 'rt') as csvfile4:
    # Csv-file with information on each novel, columns: Book_ID, Title, Author, Publisher, Perspective (1stpers, 3rdpers, multi, other)
    BOOKS_complete = csv.reader(csvfile1, delimiter=',')
    # Csv-file with information on characters, columns: Book-ID, Character-ID, Name, Gender, Descent_country, Descent_city, Living_country, Living_city, Age, Education, Profession
    NODES_complete = csv.reader(csvfile2, delimiter=';')
    # Csv-file with information on character relations, columns: Book-ID, Source, Target, Relation-type
    EDGES_complete = csv.reader(csvfile3, delimiter=',')
    # Csv-file with information on name variances, columns: Book-ID, Character-ID, Name-ID, Name-variances
    NAMES_complete = csv.reader(csvfile4, delimiter=',')

# 3. RANDOMIZE NODE ATTRIBUTES

    df_NODES = pd.read_csv(csvfiles['nodes'], sep=';')
    gender = df_NODES['gender']
    random_gender = np.random.permutation(len(gender))
    df_NODES['gender'] = gender[random_gender].values
    df_NODES = df_NODES.fillna(99)
    df_NODES.gender = df_NODES.gender.astype(int)

    descent_country = df_NODES['descent_country']
    random_descent_country = np.random.permutation(len(descent_country))
    df_NODES['descent_country'] = descent_country[random_descent_country].values
    df_NODES = df_NODES.fillna(99)
    df_NODES.descent_country = df_NODES.descent_country.astype(int)

    descent_city = df_NODES['descent_city']
    random_descent_city = np.random.permutation(len(descent_city))
    df_NODES['descent_city'] = descent_city[random_descent_city].values
    df_NODES = df_NODES.fillna(99)
    df_NODES.descent_city = df_NODES.descent_city.astype(int)

    living_country = df_NODES['living_country']
    random_living_country = np.random.permutation(len(living_country))
    df_NODES['living_country'] = living_country[random_living_country].values
    df_NODES = df_NODES.fillna(99)
    df_NODES.living_country = df_NODES.living_country.astype(int)

    living_city = df_NODES['living_city']
    random_living_city = np.random.permutation(len(living_city))
    df_NODES['living_city'] = living_city[random_living_city].values
    df_NODES = df_NODES.fillna(99)
    df_NODES.living_city = df_NODES.living_city.astype(int)

    age = df_NODES['age']
    random_age = np.random.permutation(len(age))
    df_NODES['age'] = age[random_age].values
    df_NODES = df_NODES.fillna(99)
    df_NODES.age = df_NODES.age.astype(int)

    education = df_NODES['education']
    random_education = np.random.permutation(len(education))
    df_NODES['education'] = education[random_education].values
    df_NODES = df_NODES.fillna(99)
    df_NODES.education = df_NODES.education.astype(int)

    # print (df_NODES)
    # print (df_NODES.head())
    # print (df_NODES.tail())


# 4. CREATE BOOK OBJECTS, CHARACTER OBJECTS, ADD NAME VARIANTS TO CHARACTER OBJECTS IN BOOKS OBJECTS, ADD EDGES TO NETWORK OBJECTS IN BOOK OBJECTS

    allbooks = {}

    for line in BOOKS_complete: 
        """ Creates instances of Book for every novel in the corpus

        """
        book_id = line[0]

        if book_id.isdigit(): # Check if book_id a digit

            title = line[1]
            name_author = line[2]
            gender_author = line[3]
            age_author = line[4]
            publisher = line[5]
            perspective = line[6]
            filename = line[7]

            allbooks[book_id] = Book(book_id, title, name_author, gender_author, age_author, publisher, perspective, filename)

    for row in df_NODES.itertuples():
        """ Creates instances of Character for every character in the corpus and adds them to instances of Book

        """

        book_id = row.book_id
        book_id = str(book_id)
        #print (book_id)
        character_id = row.character_id
        character_id = str(character_id)
        #print (character_id)
        name = row.name
        name = str(name)
        #print (name)
        gender = row.gender
        gender = str(gender)
        #print (gender)
        descent_country = row.descent_country
        descent_country = str(descent_country)
        #print (descent_country)
        descent_city = row.descent_city
        descent_city = str(descent_city)
        #print (descent_city)
        living_country = row.living_country
        living_country = str(living_country)
        #print (living_country)
        living_city = row.living_city
        living_city = str(living_city)
        #print (living_city)
        age = row.age
        age = str(age)
        #print (age)
        education = row.education
        education = str(education)
        #print (education)
        # profession = row.profession
        # profession = str(profession)

        allbooks[book_id].addcharacter(book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education)


    for line in NAMES_complete:
        """ Adds name variants to instances of Character in instances of Book 

        """
        book_id = line[0]

        if book_id.isdigit(): # Check if book_id is a digit

            character_id = line[1]
            name = line[2]
            name_variant = line[3]

            if allbooks[book_id].allcharacters[character_id].name != name:
                print ('NAMES_COMPLETE DOES NOT CORRESPOND WELL WITH NODES_COMPLETE!!!') # Raise error if there are mistakes or typo's in the two corresponding csv-files
                print (allbooks[book_id].allcharacters[character_id].name, name) # Print instance to which the error is due
                exit(1)


            allbooks[book_id].allcharacters[character_id].addnamevariant(name_variant)


    for line in EDGES_complete:
        """ Add edges to instances of Network in instances of Book 

        """
        book_id = line[0]

        if book_id.isdigit(): # Check if book_id is a digit

            source = line[1]
            target = line[2]
            relation_type = line[3]


            allbooks[book_id].network.add_edge(source, target, relation_type)


    # 4. OUTPUT

    bookids = sorted(allbooks.keys(),key=int)
    tasksize = len(bookids) / total
    startnr = int((task-1) * tasksize)
    endnr = int((task) * tasksize)

    taskbookids = bookids[startnr:endnr]

    csvfile = 'character_rankings.csv'
    if total > 1:
        csvfile = 'character_rankings_task_'+str(task)+'.csv'

    csvfile2 = 'networkstats_permutation.csv'
    if total > 1:
        csvfile2 = 'networkstats_permutation_task_'+str(task)+'.csv'

    csvfile3 = 'communities_frequency_distributions.csv'
    if total > 1:
        csvfile3 = 'communities_frequency_distributions_task_'+str(task)+'.csv'

    gephi_file = 'networkx_graph.gexf'
    if total > 1:
        gephi_file = 'networkx_graph_task_'+str(task)+'.gexf'


    gender_assortativity_values = []
    age_assortativity_values = []
    education_assortativity_values = []
    descent_recode_assortativity_values = []

    for book_id in taskbookids: 
        """ Computes all necessary steps for the construction of character networks and outputs centrality values per character to new csv file


        """

        print('computing network of book '+str(book_id))
        allbooks[book_id].readfile(bookpath[allbooks[book_id].perspective]) # Call method readfile on Book objects with perspective (1, 2, 3)

        allbooks[book_id].novel_word_count() # Call method novel_word_count on each Book object

        allbooks[book_id].compute_network() # Computes weight of relations between Characters objects in Book objects
        
        #allbooks[book_id].write_to_csv(csvfile) # Writes to a csv file all character info + their scores for the 5 centrality measures

        allbooks[book_id].network.compute_networkstats(csvfile2)

        #allbooks[book_id].network.detect_communities(csvfile3)

        #allbooks[book_id].network.draw_network(gephi_file)

        gender_assortativity_values.append(allbooks[book_id].network.gender_assortativity)
        age_assortativity_values.append(allbooks[book_id].network.age_assortativity)
        education_assortativity_values.append(allbooks[book_id].network.education_assortativity)
        descent_recode_assortativity_values.append(allbooks[book_id].network.descent_recode_assortativity)


    mean_gender_assortativity = sum(gender_assortativity_values)/len(gender_assortativity_values)
    #print ('mean gender assortativity', mean_gender_assortativity)
    mean_age_assortativity = sum(age_assortativity_values)/len(age_assortativity_values)
    #print ('mean age assortativity', mean_age_assortativity)
    mean_education_assortativity = sum(education_assortativity_values)/len(education_assortativity_values)
    #print ('mean education assortativity', mean_education_assortativity)
    mean_descent_recode_assortativity = sum(descent_recode_assortativity_values)/len(descent_recode_assortativity_values)
    #print ('mean descent assortativity', mean_descent_recode_assortativity)
   

    # print ('gender_assortativity_values =', gender_assortativity_values)
    # print ('age_assortativity_values =', age_assortativity_values)
    # print ('education_assortativity_values =', education_assortativity_values)
    # print ('descent_recode_assortativity_values =', descent_recode_assortativity_values)

































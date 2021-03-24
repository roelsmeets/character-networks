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
import os
import glob
import sys
import errno
import csv
from characternetworks import Book, Character, Network, Character_Centrality

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

    
# 3. CREATE BOOK OBJECTS, CHARACTER OBJECTS, ADD NAME VARIANTS TO CHARACTER OBJECTS IN BOOKS OBJECTS, ADD EDGES TO NETWORK OBJECTS IN BOOK OBJECTS

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

    for line in NODES_complete:
        """ Creates instances of Character for every character in the corpus and adds them to instances of Book

        """
        book_id = line[0]


        if book_id.isdigit(): # Check if book_id is a digit

            character_id = line[1]
            name = line[2]
            gender = line[3]
            descent_country = line[4]
            descent_city = line[5]
            living_country = line[6]
            living_city = line[7]
            age = line[8]
            education = line[9]
            profession = line[10]

            allbooks[book_id].addcharacter(book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession)


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

    csvfile2 = 'networkstats.csv'
    if total > 1:
        csvfile2 = 'networkstats_task_'+str(task)+'.csv'

    csvfile3 = 'communities_frequency_distributions.csv'
    if total > 1:
        csvfile3 = 'communities_frequency_distributions_task_'+str(task)+'.csv'

    gephi_file = 'networkx_graph.gexf'
    if total > 1:
        gephi_file = 'networkx_graph_task_'+str(task)+'.gexf'



    teachers = []
    gender_distribution_teachers = {'male': 0, 'female': 0, 'unknown': 0}
    descent_country_distribution_teachers = {'Nederland': 0, 'Belgie': 0, 'Europees': 0, 'Westers': 0, 'Midden Oosten': 0, 'Overig': 0, 'Onbekend': 0}
    descent_recode_distribution_teachers = {'Autochtoon': 0, 'Allochtoon': 0, 'Onbekend': 0}

    # descent_city_distribution_teachers =  {'Amsterdam': 1, 'Randstad': 2, 'Buiten de Randstad': 3, 'Grote stad in Vlaanderen (Brussel/ Antwerpen/ Gent)': 4, 'Elders in Belgie': 5, 'Grote stad in Europa': 6, 'Elders in Europa': 7, 'Stad in Midden Oosten': 8, 'Dorp in Midden Oosten': 9, 'Stad in VS': 10, 'Dorp in VS': 11, 'Stad Elders': 12, 'Dorp elders': 13}
    # residence_country_distribution_teachers = {'Nederland': 0, 'Belgie': 0, 'Europees': 0, 'Westers': 0, 'Midden Oosten': 0, 'Overig': 0, 'Onbekend': 0}
    # residence_city_distribution_teachers =  {'Amsterdam': 1, 'Randstad': 2, 'Buiten de Randstad': 3, 'Grote stad in Vlaanderen (Brussel/ Antwerpen/ Gent)': 4, 'Elders in Belgie': 5, 'Grote stad in Europa': 6, 'Elders in Europa': 7, 'Stad in Midden Oosten': 8, 'Dorp in Midden Oosten': 9, 'Stad in VS': 10, 'Dorp in VS': 11, 'Stad Elders': 12, 'Dorp elders': 13}

    education_distribution_teachers = {'Hoogopgeleid': 0, 'Laagopgeleid': 0, 'Onbekend': 0}
    age_distribution_teachers = {'<25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-64': 0, '65+': 0, 'Onbekend': 0}

    for book_id in taskbookids: 
        """ Computes all necessary steps for the construction of character networks and outputs centrality values per character to new csv file


        """

        print('computing network of book '+str(book_id))
        allbooks[book_id].readfile(bookpath[allbooks[book_id].perspective]) # Call method readfile on Book objects with perspective (1, 2, 3)

        allbooks[book_id].novel_word_count() # Call method novel_word_count on each Book object

        allbooks[book_id].compute_network() # Computes weight of relations between Characters objects in Book objects
        
        #allbooks[book_id].write_to_csv(csvfile) # Writes to a csv file all character info + their scores for the 5 centrality measures


        #allbooks[book_id].network.compute_networkstats(csvfile2)

        #allbooks[book_id].network.detect_communities(csvfile3)

        #allbooks[book_id].network.draw_network(gephi_file)


        for character in allbooks[book_id].allcharacters.values():

            #print ('degree of', character.character_id, 'in', character.book_id, '=', character.degree)


            if 'docent' in character.profession or 'leraar' in character.profession or 'lerares' in character.profession:
                teachers.append(character)

    for teacher in teachers:
        if teacher.gender == '1':
            gender_distribution_teachers['male'] += 1
        elif teacher.gender == '2':
            gender_distribution_teachers['female'] += 1
        elif teacher.gender == '99':
            gender_distribution_teachers['unknown'] += 1


        if teacher.descent_country == '1':
            descent_country_distribution_teachers['Nederland'] += 1
        elif teacher.descent_country == '2':
            descent_country_distribution_teachers['Belgie'] += 1
        elif teacher.descent_country == '3':
            descent_country_distribution_teachers['Europees'] += 1
        elif teacher.descent_country == '4':
            descent_country_distribution_teachers['Westers'] += 1
        elif teacher.descent_country == '5':
            descent_country_distribution_teachers['Midden Oosten'] += 1
        elif teacher.descent_country == '6':
            descent_country_distribution_teachers['Overig'] += 1
        elif teacher.descent_country == '99':
            descent_country_distribution_teachers['Onbekend'] += 1

        if (teacher.descent_country == '1') or (teacher.descent_country== '2'):
            descent_recode_distribution_teachers['Autochtoon'] += 1 # Recode 1 (Dutch) and 2 (Belgian) into 'Autochtoon'
        if (teacher.descent_country == '3') or (teacher.descent_country =='4') or (teacher.descent_country =='5') or (teacher.descent_country =='6'):
            descent_recode_distribution_teachers['Allochtoon'] += 1 # Recode 3 (European), 4 (Western), 5 (Middle Eastern), 6 (Other) into 'Allochtoon'
        if teacher.descent_country == '99':
            descent_recode_distribution_teachers['Onbekend'] += 1  # 99 (unknown) remains the same

   
        if teacher.education == '1':
            education_distribution_teachers['Hoogopgeleid'] += 1
        elif teacher.education == '2':
            education_distribution_teachers['Laagopgeleid'] += 1
        elif teacher.education == '99':
            education_distribution_teachers['Onbekend'] += 1

        if teacher.age == '1':
            age_distribution_teachers['<25'] += 1
        elif teacher.age == '2':
            age_distribution_teachers['26-35'] += 1
        elif teacher.age == '3':
            age_distribution_teachers['36-45'] += 1
        elif teacher.age == '4':
            age_distribution_teachers['46-55'] += 1
        elif teacher.age == '5':
            age_distribution_teachers['56-64'] += 1
        elif teacher.age == '6':
            age_distribution_teachers['65+'] += 1
        elif teacher.age == '99':
            age_distribution_teachers['Onbekend'] += 1

    # print ('male teachers', gender_distribution_teachers['male'])
    # print ('female teachers', gender_distribution_teachers['female'])
    # print ('unknown gender teachers', gender_distribution_teachers['unknown'])

    # print ('Nederlandse roots', descent_country_distribution_teachers['Nederland'])
    # print ('Belgische roots', descent_country_distribution_teachers['Belgie'])
    # print ('Europese roots', descent_country_distribution_teachers['Europees'])
    # print ('Westerse roots', descent_country_distribution_teachers['Westers'])
    # print ('Midden Oosterse roots', descent_country_distribution_teachers['Midden Oosten'])
    # print ('Roots overig', descent_country_distribution_teachers['Overig'])
    # print ('Roots onbekend', descent_country_distribution_teachers['Onbekend'])

    # print ('Autochtoon', descent_recode_distribution_teachers['Autochtoon'])
    # print ('Allochtoon', descent_recode_distribution_teachers['Allochtoon'])
    # print ('Onbekend', descent_recode_distribution_teachers['Onbekend'])


    # print ('Hoogopgeleid', education_distribution_teachers['Hoogopgeleid'])
    # print ('Laagopgeleid', education_distribution_teachers['Laagopgeleid'])
    # print ('Onbekend', education_distribution_teachers['Onbekend'])

    # print ('<25', age_distribution_teachers['<25'])
    # print ('26-35', age_distribution_teachers['26-35'])
    # print ('36-45', age_distribution_teachers['36-45'])
    # print ('46-55', age_distribution_teachers['46-55'])
    # print ('56-64', age_distribution_teachers['56-64'])
    # print ('65+', age_distribution_teachers['65+'])
    # print ('Onbekend', age_distribution_teachers['Onbekend'])

    print ('Gender dict:', gender_distribution_teachers)
    print ('Descent country dict:', descent_country_distribution_teachers)
    print ('Descent recode dict:', descent_recode_distribution_teachers)
    print ('Education dict:', education_distribution_teachers)
    print ('Age dict:', age_distribution_teachers)

    
    gender_nr_teachers = 0

    for key, value in gender_distribution_teachers.items():
        gender_nr_teachers += value

    print ('gender nr teachers:', gender_nr_teachers)

    gender_dataframe = pd.DataFrame.from_dict(gender_distribution_teachers, orient='index', columns= ['gender'])
    print (gender_dataframe)
    print('relative distribution gender:', gender_dataframe / gender_nr_teachers) 
    print ('#######################################################')



    descent_country_nr_teachers = 0

    for key, value in descent_country_distribution_teachers.items():
        descent_country_nr_teachers += value

    print ('descent_country_nr_teachers:', descent_country_nr_teachers)

    descent_country_dataframe = pd.DataFrame.from_dict(descent_country_distribution_teachers, orient='index', columns= ['descent country'])
    print (descent_country_dataframe)
    print('relative distribution descent_country', descent_country_dataframe / descent_country_nr_teachers)
    print ('#######################################################')




    descent_recode_nr_teachers = 0

    for key, value in descent_recode_distribution_teachers.items():
        descent_recode_nr_teachers += value

    print ('descent_recode_nr_teachers:', descent_recode_nr_teachers)

    descent_recode_dataframe = pd.DataFrame.from_dict(descent_recode_distribution_teachers, orient='index', columns= ['descent recode'])
    print (descent_recode_dataframe)
    print('relative distribution descent_recode', descent_recode_dataframe / descent_recode_nr_teachers)
    print ('#######################################################')
 



    education_nr_teachers = 0

    for key, value in education_distribution_teachers.items():
        education_nr_teachers += value

    print ('education_nr_teachers:', education_nr_teachers)

    education_dataframe = pd.DataFrame.from_dict(education_distribution_teachers, orient='index', columns= ['education'])
    print (education_dataframe)
    print('relative distribution education', education_dataframe / education_nr_teachers)
    print ('#######################################################')
 



    age_nr_teachers = 0

    for key, value in age_distribution_teachers.items():
        age_nr_teachers += value

    print ('age_nr_teachers:', age_nr_teachers)

    age_dataframe = pd.DataFrame.from_dict(age_distribution_teachers, orient='index', columns= ['age'])
    print (age_dataframe)
    print('relative distribution age', age_dataframe / age_nr_teachers)
    print ('#######################################################')


    with open ('teachers_stats', 'a', newline='') as f:
        csvwriter = csv.writer(f)

        for teacher in teachers:
            csvwriter.writerow([teacher.book_id, teacher.character_id, teacher.gender, teacher.descent_country, teacher.education, teacher.age, teacher.degree, teacher.betweenness, teacher.closeness, teacher.eigenvector, teacher.katz])








 
























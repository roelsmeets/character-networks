# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# 1. IMPORTS

from characternetworks import Character, Character_Centrality
from variables import *

import csv




# 2. INPUT

allcharacters = {}

with open(csvfiles['rankings'], 'rt') as csvfile1, \
     open(csvfiles['edges'], 'rt') as csvfile2:
    RANKINGS = csv.reader(csvfile1, delimiter=',')
    EDGES_complete = csv.reader(csvfile2, delimiter=',')


    for line in RANKINGS:
        """ Read the rankings file

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
            degree = line[11]
            betweenness = line[12]
            closeness = line[13]
            eigenvector = line[14]
            katz = line[15]

            if not book_id in allcharacters:
                allcharacters[book_id] = {}
            allcharacters[book_id][character_id] = Character_Centrality(book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession, degree, betweenness, closeness, eigenvector, katz)




# 3. COMPUTE SOCIAL BALANCE

    """
        Testing the social balance theory of social psychologist Fritz Heider (1946) for all enemy/friend triads in the corpus. 

        Categories of social balance:

        Balance = 
                enemy (-) enemy (- ) friend (+) 
                    OR
                friend (+) friend (+) friend (+)

        Imbalance = 
                friend (+) friend (+) enemy (-) 
                    OR 
                enemy(-) enemy (-) enemy (- )


    """
    
    balance = 0
    imbalance = 0

    enemypairs = {} 
    friendpairs = {}
    friends = {}
    enemies = {}
    relation_types = {}

    for line in EDGES_complete:
        """ Read the edges file

        """
        
        book_id = line[0]

        if not book_id in enemypairs:
            enemypairs[book_id] = []
        if not book_id in enemies:
            enemies[book_id] = {}

        if not book_id in friendpairs:
            friendpairs[book_id] = []
        if not book_id in friends:
            friends[book_id] = {}

        if not book_id in relation_types:
            relation_types[book_id] = {}



        if book_id.isdigit(): # Check if book_id is a digit

            source = line[1]
            target = line[2]
            relation_type = line[3]


            relation_types[book_id][(source, target)] = relation_type

           
            #enemyfound = 0

            if relation_type.find('vijand') > -1:
                #print (relation_type,relation_type.find('vijand'))
                #enemyfound += 1
                #print ('Found:', enemyfound, 'enemies')
                if not (target,source) in enemypairs[book_id]:
                    enemypairs[book_id].append((source,target))
                if not source in enemies[book_id]:
                    enemies[book_id][source] = []
                enemies[book_id][source].append(target)

            #friendfound = 0

            if relation_type.find('vriend') > -1:
                #friendfound += 1
                #print ('Found:', friendfound, 'friends')
                if not (target,source) in friendpairs[book_id]:
                    friendpairs[book_id].append((source,target))
                if not source in friends[book_id]:
                    friends[book_id][source] = []
                friends[book_id][source].append(target)



    tripletsseen = {}

    for book_id in enemypairs:
        for (source, target) in enemypairs[book_id]:
            try:
                for enemy in enemies[book_id][source]:
                    if enemy in enemies[book_id][target]:
                    	triplet = book_id+",".join(sorted([source,target,enemy]))
                    	if not triplet in tripletsseen:
                    		imbalance += 1
                    		#print ('1: falsified',book_id,source,target,enemy,relation_types[book_id][(source,target)],relation_types[book_id][(source,enemy)],relation_types[book_id][(enemy,target)])
                    		tripletsseen[triplet] = True
                if source in friends[book_id] and target in friends[book_id]:
                    for friend in friends[book_id][source]:
                        if friend in friends[book_id][target]:
                        	triplet = book_id+",".join(sorted([source,target,friend]))
                        	if not triplet in tripletsseen:
                        		imbalance += 1
                        		#print ('2: falsified',book_id,source,target,friend,relation_types[book_id][(source,target)],relation_types[book_id][(source,friend)],relation_types[book_id][(friend,target)])
                        		tripletsseen[triplet] = True
            except:
                print('ERROR:',book_id,source,target)

    for book_id in friendpairs:
        for (source, target) in friendpairs[book_id]:
            try:
                if source in enemies[book_id] and target in enemies[book_id]:
                    for enemy in enemies[book_id][source]:
                        if enemy in enemies[book_id][target]:
                        	triplet = book_id+",".join(sorted([source,target,enemy]))
                        	if not triplet in tripletsseen:
                        		balance += 1
                        		#print ('3: verified',book_id,source,target,enemy,relation_types[book_id][(source,target)],relation_types[book_id][(source,enemy)],relation_types[book_id][(enemy,target)])
                        		tripletsseen[triplet] = True
                    for friend in friends[book_id][source]:
                        if friend in friends[book_id][target]:
                        	triplet = book_id+",".join(sorted([source,target,friend]))
                        	if not triplet in tripletsseen:
                        		balance += 1
                        		#print ('4: verified',book_id,source,target,friend,relation_types[book_id][(source,target)],relation_types[book_id][(source,friend)],relation_types[book_id][(friend,target)])
                        		tripletsseen[triplet] = True
            except:
                print('ERROR:',book_id,source,target)

    print ('Balanced triads =', balance)
    print ('Imbalanced triads =', imbalance)


# 4. COMPUTE ENEMY HIERARCHIES

    """
        Modelling 'conflict scores' for all enemy dyads in the corpus. 
        Each Character_Centrality class object (see characternetworks.py) has five conflictscore attributes, one for each measure

        Steps:
        - Check for every two enemies (enemypairs) who has a higher score on centrality measures (degree, betweenness, closeness, eigenvector, katz)
        - In case a character has a higher score, increment the conflictscore for each measure by one 
        - Output all metadata for enemies + their conflictscores to character-rankings_conflictscore.csv (to be used in multiple linear regression in SPSS)
        
    """

    
    with open ('character-rankings_conflictscore', 'a', newline='') as csvoutput:
        csvwriter = csv.writer(csvoutput, lineterminator='\n') 

        for book_id in allcharacters:
            for character_id in allcharacters[book_id]:
                if character_id in enemies[book_id]:
                    #print(book_id,character_id)
                    for enemy in enemies[book_id][character_id]:
                        for measure in allcharacters[book_id][character_id].conflictscore:
                            #rint(measure)
                            if getattr(allcharacters[book_id][character_id],measure) > getattr(allcharacters[book_id][enemy],measure): # For every two enemies, a character's conflictscore is incremented by one when he/she is more central than his enemy
                                allcharacters[book_id][character_id].conflictscore[measure] += 1
                            #print (allcharacters[book_id][character_id].conflictscore[measure])

        for book_id in allcharacters:
            for character_id in allcharacters[book_id]:
                if character_id in enemies[book_id]:
                    # Write to a csv file all metadata (+ conflictscores for every centrality measure) for characters that are enemies 
                    csvwriter.writerow([book_id, \
                                character_id, \
                                allcharacters[book_id][character_id].name, \
                                allcharacters[book_id][character_id].gender, \
                                allcharacters[book_id][character_id].descent_country, \
                                allcharacters[book_id][character_id].descent_city, \
                                allcharacters[book_id][character_id].living_country, \
                                allcharacters[book_id][character_id].living_city, \
                                allcharacters[book_id][character_id].age, \
                                allcharacters[book_id][character_id].education, \
                                allcharacters[book_id][character_id].profession, \
                                allcharacters[book_id][character_id].degree, \
                                allcharacters[book_id][character_id].betweenness, \
                                allcharacters[book_id][character_id].closeness, \
                                allcharacters[book_id][character_id].eigenvector, \
                                allcharacters[book_id][character_id].katz, \
                                allcharacters[book_id][character_id].conflictscore['degree'], \
                                allcharacters[book_id][character_id].conflictscore['betweenness'], \
                                allcharacters[book_id][character_id].conflictscore['closeness'], \
                                allcharacters[book_id][character_id].conflictscore['eigenvector'], \
                                allcharacters[book_id][character_id].conflictscore['katz']])
                                

        # print ('Degree:', allcharacters['3']['4'].conflictscore['degree'])
        # print ('Betweennes:',allcharacters['3']['4'].conflictscore['betweenness'])
        # print ('Closeness:', allcharacters['3']['4'].conflictscore['closeness'])
        # print ('Eigenvector:', allcharacters['3']['4'].conflictscore['eigenvector'])
        # print ('Katz:', allcharacters['3']['4'].conflictscore['katz'])

    





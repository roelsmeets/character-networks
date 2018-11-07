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

            winlose = 0 

            if not book_id in allcharacters:
                allcharacters[book_id] = {}
            allcharacters[book_id][character_id] = Character_Centrality(book_id, character_id, name, gender, descent_country, descent_city, living_country, living_city, age, education, profession, degree, betweenness, closeness, eigenvector, katz, winlose)


# 3. COMPUTE SOCIAL BALANCE
    
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




    for book_id in enemypairs:
        #for enemypair in enemypairs[book_id]:
            #print (book_id, enemypair)
        for (source, target) in enemypairs[book_id]:
            try:
                for enemy in enemies[book_id][source]:
                    if enemy in enemies[book_id][target]:
                        imbalance += 1
                        print ('1: falsified',book_id,source,target,enemy,relation_types[book_id][(source,target)],relation_types[book_id][(source,enemy)],relation_types[book_id][(enemy,target)])
                if source in friends[book_id] and target in friends[book_id]:
                    for friend in friends[book_id][source]:
                        if friend in friends[book_id][target]:
                            imbalance += 1
                            print ('2: falsified',book_id,source,target,friend,relation_types[book_id][(source,target)],relation_types[book_id][(source,friend)],relation_types[book_id][(friend,target)])
            except:
                print('ERROR:',book_id,source,target)

    for book_id in friendpairs:
        for (source, target) in friendpairs[book_id]:
            try:
                if source in enemies[book_id] and target in enemies[book_id]:
                    for enemy in enemies[book_id][source]:
                        if enemy in enemies[book_id][target]:
                            balance += 1
                            print ('3: verified', book_id,source,target,enemy,relation_types[book_id][(source,target)],relation_types[book_id][(source,enemy)],relation_types[book_id][(enemy,target)])
                    for friend in friends[book_id][source]:
                        if friend in friends[book_id][target]:
                            balance += 1
                            print ('4: verified',book_id,source,target,friend, relation_types[book_id][(source,target)],relation_types[book_id][(source,friend)],relation_types[book_id][(friend,target)])
            except:
                print('ERROR:',book_id,source,target)

    print ('Balanced triads =', balance)
    print ('Imbalanced triads =', imbalance)


# 4. COMPUTE ENEMY HIERARCHIES



    # Strategy 1 
    for book_id in allcharacters:
        for character_id in allcharacters[book_id]:
            for (source, target) in enemypairs[book_id]:
                if allcharacters[source] and allcharacters[target] in enemypairs[book_id]:
                    # print ('source:', allcharacters[source])
                    # print ('target:', allcharacters[target])
                    if allcharacters[book_id][source].degree > allcharacters[book_id][target].degree:
                        allcharacters[book_id][source].winlose += 1
                    print ('book_id source =', allcharacters[book_id][source].book_id, 'character_id source =', allcharacters[book_id][source].character_id, 'degree source =', allcharacters[book_id][source].degree,  'source winlose score degree=', allcharacters[book_id][source].winlose)
                    if allcharacters[book_id][target].degree > allcharacters[book_id][source].degree:
                        allcharacters[book_id][target].winlose += 1
                        print ('book_id target =', allcharacters[book_id][target].book_id, 'character_id target =', allcharacters[book_id][target].character_id, 'degree target =', allcharacters[book_id][target].degree,  'target winlose score degree=', allcharacters[book_id][target].winlose)



    

    
    # Strategy 2
    # for book_id in enemypairs:
    #     for (source, target) in enemypairs[book_id]:
    #         for character_id in allcharacters[book_id][source]:
    #             if character_id in allcharacters[book_id][target]































    












# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

from characternetworks import Character, Character_Centrality
from variables import *

import csv

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
						print ('1: falsified',book_id,source,target,enemy,relation_types[book_id][(source,target)],relation_types[book_id][(source,enemy)],relation_types[book_id][(enemy,target)])
				if source in friends[book_id] and target in friends[book_id]:
					for friend in friends[book_id][source]:
						if friend in friends[book_id][target]:
							print ('2: falsified',book_id,source,target,friend,relation_types[book_id][(source,target)],relation_types[book_id][(source,friend)],relation_types[book_id][(friend,target)])
			except:
				print('ERROR:',book_id,source,target)

	for book_id in friendpairs:
		for (source, target) in friendpairs[book_id]:
			try:
				if source in enemies[book_id] and target in enemies[book_id]:
					for enemy in enemies[book_id][source]:
						if enemy in enemies[book_id][target]:
							print ('3: verified', book_id,source,target,enemy,relation_types[book_id][(source,target)],relation_types[book_id][(source,enemy)],relation_types[book_id][(enemy,target)])
					for friend in friends[book_id][source]:
						if friend in friends[book_id][target]:
							print ('4: verified',book_id,source,target,friend, relation_types[book_id][(source,target)],relation_types[book_id][(source,friend)],relation_types[book_id][(friend,target)])
			except:
				print('ERROR:',book_id,source,target)










	












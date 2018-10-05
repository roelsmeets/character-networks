# character-networks
Making social networks from fictional characters in literature

Object-Oriented model written in Python, with three main classes: Character, Book, Network. 

Four interlinked databases:
  BOOKS_complete.csv contains all info on 170 contemporary Dutch novels
  NODES_complete.csv contains all demographic info on 2137 characters in those novels
  NAMES_complete.csv contains all name variants of those characters
  EDGES_complete.csv contains all relational info between those characters
  
Python scripts:
   characternetworks.py contains the three classes 
   Superscript.py computes character networks, ranks all characters, and output the results to character-rankings.csv
   conflict.py models triads of characters by looking at enemy/friend relations
  
  

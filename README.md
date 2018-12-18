# character-networks
Making social networks from fictional characters in literature

Object-Oriented model written in Python, with three main classes: Character, Book, Network. 

Four interlinked databases:
* BOOKS_complete.csv contains all info on 170 contemporary Dutch novels
* NODES_complete.csv contains all demographic info on 2137 characters in those novels
* NAMES_complete.csv contains all name variants of those characters
* EDGES_complete.csv contains all relational info between those characters
  
Python scripts:
* characternetworks.py contains the three classes Character, Book, and Network
* Superscript.py computes character networks, ranks all characters, and output the results to character-rankings.csv
* conflict.py models enemy/friend relations between characters on two levels:
  1. enemy/friend triads: tests Heider's social balance theory based on enemies and friends in the corpus
  2. enemy dyads: computes hierarchies between every two enemies based on a 'conflictscore' (one for each measure)

 Csv output:
 * character-rankings.csv (output from Superscript.py)
 * character-rankings_conflictscore.csv (output from conflict.py)

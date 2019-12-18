# #!/usr/bin/env python

# # -*- coding: utf-8 -*-


bookpath = {}
bookpath['1'] = '/Users/roelsmeets/desktop/corpus_1stpers_clean'
bookpath['2'] = '/Users/roelsmeets/desktop/corpus_3rdpers_clean'
bookpath['3'] = '/Users/roelsmeets/desktop/corpus_multi_clean_annotated' 
bookpath['4'] = '/Users/roelsmeets/desktop/corpus_other_clean'

csvpath = '/Users/roelsmeets/desktop/Libris_networks'
csvfiles = {}
csvfiles['books'] = csvpath + '/BOOKS_complete/BOOKS_complete.csv'
csvfiles['nodes'] = csvpath + '/NODES_complete/NODES_complete.csv'
csvfiles['edges'] = csvpath + '/EDGES_complete/EDGES_complete.csv'
csvfiles['names'] = csvpath + '/NAMES_complete/NAMES_complete.csv'
csvfiles['rankings'] = csvpath + '/character-networks/character-rankings.csv'


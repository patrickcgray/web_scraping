'''
Created on Feb 6, 2013

@author: clifgray
'''

import pickle

main_path = 'output/images.txt'

main_file = open(main_path, 'r')
stored_pictures = pickle.load(main_file)
main_file.close()

for pic in stored_pictures:
    print """<br><img src='""" + pic + """'>"""
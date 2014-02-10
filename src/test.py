'''
Created on Feb 6, 2013

@author: clifgray
'''
import httplib, urllib2

from BeautifulSoup import BeautifulSoup

def soupify_url(url):
    try:
        html = urllib2.urlopen(url).read()
    except:
        print 'somethin wrong with the url or opening it'
    return BeautifulSoup.BeautifulSoup(html)

link_text_list = []

the_url = 'http://www.reddit.com/r/motorcycles'

soup = soupify_url(the_url) 

all_text = soup.getText()

keyword_list = ['motorcycle', 'motorcycles', 'bike', 'cycle', 'dirtbike']
counter = 0
for item in keyword_list:
      if item in all_text:
            counter += 1
print counter

            
    



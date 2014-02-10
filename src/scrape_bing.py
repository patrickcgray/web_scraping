'''
Created on Feb 8, 2013

@author: clifgray
'''

import urllib2, urlparse, httplib
from BeautifulSoup import BeautifulSoup
from collections import deque

link_text_list = []

def get_link_text_list(keywords):
    the_url = 'http://www.bing.com/search?q='
    for keyword in keywords:
        the_url = the_url + '+' + keyword

    soup = soupify_url(the_url) 
    
    #splitting up all the results and iterating through them
    for tag in soup.findAll('li'):
        the_class = tag.get('class')
        #limiting it to the actual result class
        if the_class == 'sa_wr':
            list_in_a_list = [1, 2]
            tag = str(tag)
            result = BeautifulSoup.BeautifulSoup(tag)
            #finding the urls in the result
            for link in result.findAll('a'):
                url = link.get('href')
                list_in_a_list[0] = (url)
            texts = result.findAll(text=True)
            relevant_text = ' '.join(texts)
            try:
                list_in_a_list[1] = relevant_text
            except UnicodeError:
                something = None
            link_text_list.append(list_in_a_list)
            
    return link_text_list, the_url

def get_links(keywords, a_list=True):
    link_list = None
    if a_list:
        link_list = []
    else:
        link_list = deque([])
    
    link_text_list, the_url = get_link_text_list(keywords)
        
    try:
        for inner_list in link_text_list:
            link_list.append(inner_list[0])
    except TypeError:
        print 'didnt get a list'
    
    return link_list, the_url
            
def soupify_url(url):
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError:
        print "error in soupifying"
        return 
    except ValueError:
        print "error in soupifying"
        return
    except httplib.InvalidURL:
        print "error in soupifying"
        return
    except httplib.BadStatusLine:
        print "error in soupifying"
        return
            
    return BeautifulSoup.BeautifulSoup(html)
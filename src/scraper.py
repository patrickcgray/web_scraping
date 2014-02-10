'''
Created on Feb 6, 2013

@author: clifgray
'''

import urllib2, urlparse, httplib, pickle
import imageInfo, scrape_bing
from BeautifulSoup import BeautifulSoup
from collections import deque

visited_pages = []
visit_queue = deque([])
collected_pages = []
collected_pics = []

count = 0
pic_count = 0

def scrape_pages(url, root_url, keywords=[], recurse=True):
    #variables
    max_count = 25
    pic_num = 100
    
    global count
    global pic_count
    global collected_pics
    global collected_pages
    #this is all of the links that have been scraped
    the_links = []
    
    soup = soupify_url(url)
    
    #only add new pages onto the queue if the recursion argument is true    
    if recurse:
        #find all the links on the page
        try:
            for tag in soup.findAll('a'):
                the_links.append(tag.get('href'))
        except AttributeError:
            return
        
        try:
            external_links, internal_links, root_links, primary_links = categorize_links(the_links, url, root_url)
        except TypeError:
            return
        
    #    print 'current url'
    #    print url
    #    print 'external links'
    #    print external_links
    #    print 'internal links'
    #    print internal_links
    #    print 'root links'
    #    print root_links
    
        #change it so this depends on the input
        links_to_visit = external_links + internal_links + root_links
        
        #build the queue
        for link in links_to_visit:
            if link not in visited_pages and link not in visit_queue:
                visit_queue.append(link)
    
    visited_pages.append(url)
    count = count + 1
    print 'number of pages visited'
    print count
    
    #add pages to collected_pages depending on the criteria given if any keywords are given
    if keywords:
        page_to_add = find_pages(url, soup, keywords)
        
        print 'page to add'
        print page_to_add
        if page_to_add and page_to_add not in collected_pages:
            collected_pages.append(page_to_add)
        
    
    pics_to_add = add_pics(url, soup)
    print 'pics to add'
    print pics_to_add
    if pics_to_add:
        collected_pics.extend(pics_to_add)
    
    #here is where the actual recursion happens by finishing the queue
    while visit_queue:
        if count >= max_count:
            return
        
        if pic_count > pic_num:
            return
        
        link = visit_queue.popleft()
        print link
        scrape_pages(link, root_url)
        
    print '***done***'
    ###done with the recursive scraping function here

def scrape_bing_src(keywords):
    visit_queue, the_url = scrape_bing.get_links(keywords, a_list = False)
    scrape_pages(visit_queue.popleft(), the_url, keywords, recurse=True)
    
def scrape_with_links(link_list, keywords):
    for link in link_list:
        visit_queue.append(link)
    first_link = visit_queue.popleft()
    scrape_pages(first_link, first_link, keywords, recurse=True)
    
    
            
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

def categorize_links(the_links, url, root_url):
    external_links = []
    internal_links = []
    root_links = []
    primary_links = []
    
    for link in the_links:
        try:
            parsed_url = urlparse.urlparse(url)
            netloc = parsed_url.netloc
            try:
                site_name = (netloc.split('.')[1]) + '.' + (netloc.split('.')[2])
            except IndexError:
                #I am sure this is missing some important page but it is alright for now.
                return

            if 'http' in link and site_name not in link:
                external_links.append(link)
            elif site_name in link:
                internal_links.append(link)
            else:
                root_links.append('http://' + netloc + link)
                
            if root_url in link:
                primary_links.append(link)
                
        #dangerous
        except TypeError:
            something = None
            
    return external_links, internal_links, root_links, primary_links

#need to think about this and fix it up
def add_pics(url, soup):
    global pic_count
    more_pics = []
    if url[-3:] == 'jpg' or url[-3:] == 'png' or url[-3:] == 'gif':
        result = filter_pic(url)
        if result:
            more_pics.append(result)
            pic_count += 1
    
    #need to add img tags
    for tag in soup.findAll('img'):
        result = filter_pic(tag.get('src'))
        if result:
            more_pics.append(result)
            pic_count += 1
    
    return more_pics

def filter_pic(url):
    global pic_count
    try:
        file = urllib2.urlopen(url).read()
    except ValueError:
        return None
    except urllib2.HTTPError:
        return None
    except AttributeError:
        return None
    
    content_type, width, height = imageInfo.getImageInfo(file)
    if width > 200 and height > 200:
        print "added pic"
        pic_count += 1
        return url
    else:
        return None

def find_pages(url, soup, keywords):
    #collect something from the pages right here...
    #currently I am testing for keywords and adding the page to a list if they contain them
    print 'testing the page for keywords'
    all_text = soup.getText()

    counter = 0
    for item in keywords:
        if item in all_text:
            counter += 1
    if counter > 0:
        return url, counter
    else:
        return None
    
def update_pics(collected_pics, main_path, save_path):        
    stored_pictures = []
    try:
        main_file = open(main_path, 'r')
        stored_pictures = pickle.load(main_file)
        main_file.close()
    except EOFError:
        saved_file = open(save_path, 'r') 
        saved_pics = pickle.load(saved_file)
        stored_pictures = saved_pics
        saved_file.close()
    
    for pic in collected_pics:
        if pic not in stored_pictures:
            stored_pictures.append(pic)
    
    main_file = open(main_path, 'w')
    save_file = open(save_path, 'w') 
    pickle.dump(stored_pictures, main_file)
    pickle.dump(stored_pictures, save_file)
    main_file.close()
    save_file.close()

#I could find frequency of words on pages or crawl the web to see how often a page is referenced or
#I could let the users have a say in the ranking and I could take some new attributes into consideration like image quality and size and frequency of visitation

###other random functions

def countTags(soup, tag):
    tags = soup.findAll(tag)
    return tags.length    

def printText(tags):     
    for tag in tags:         
        if tag.__class__ == BeautifulSoup.BeautifulSoup.NavigableString:             
            print tag 
        else: 
            printText(tag)
            
            
###### calling the actual functions

the_url = 'http://www.reddit.com/r/motorcycles'
#call the function
#scrape_pages(the_url, the_url)

#scrape_bing_src(['motorcycle'])

scrape_with_links(['http://www.imgur.com/r/motorcycles'], ['motorcycle'])

print 'motorcycle pages'
for page in collected_pages:
    print page
    
print "pages visited"
for page in visited_pages:
    print page

print 'motorcycle pics'
for page in collected_pics:
    print page
    
update_pics(collected_pics, 'output/images.txt', 'output/saved.txt')
    
#print soup.prettify()
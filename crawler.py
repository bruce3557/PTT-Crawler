import bs4
import urllib2
import sys
import os
import re
import time
import json


board_name = sys.argv[1]

page_url = lambda n: 'http://www.ptt.cc/bbs/' + board_name + '/index' + str(n) + '.html'
post_url = lambda id: 'http://www.ptt.cc/bbs/' + board_name + '/' + id + '.html'


## fetched files will be stored under the directory "./fetched/BOARDNAME/"
path = os.path.join('fetched', board_name)
try:
    os.makedirs(path)
except:
    sys.stderr.write('Warning: "%s" already existed\n' % path)
os.chdir(path)


sys.stderr.write('Crawling "%s" ...\n' % board_name)
## determine the total number of pages for this board
print page_url(1)
page = bs4.BeautifulSoup(urllib2.urlopen(page_url(1)).read())
#num_pages = int(re.findall(' \d+ ', page.find(id='prodlist').find('h2').contents[-1])[0])
num_pages = 1
sys.stderr.write('Total number of pages: %d\n' % num_pages)

## a mapping from post_id to number of pushes
num_pushes = dict()

for n in xrange(1, num_pages + 1):

    try:
        page = bs4.BeautifulSoup(urllib2.urlopen(page_url(n)).read())
    except:
        sys.stderr.write('Error occured while fetching %s\n' % page_url(n))
        continue
    for tr in page.find_all('div', 'r-ent'):
        ## For instance: "M.1368632629.A.AF7"
        post_id = tr.contents[5].contents[1].get('href').split('/')[-1][:-5]
        ## Record the number of pushes, which is an integer from -100 to 100
        try:
          num_pushes[post_id] = tr.contents[1].contents[0].contents[0]
        except:
          num_pushes[post_id] = 0
        ## Fetch the post content
        sys.stderr.write('Fetching %s ...\n' % post_id)
        post_file = open(post_id, 'w')

        try:
            post = bs4.BeautifulSoup(urllib2.urlopen(post_url(post_id)).read())
        except:
            sys.stderr.write('Error occured while fetching %s\n' % post_url(post_id))
            continue

        for content in post.find(id='main-content').contents:
            ## u'\u25c6' is the starting character in the 'source ip line',
            ## which for instance looks like "u'\u25c6' From: 111.253.164.108"
            if type(content) is bs4.element.NavigableString and content[0] != u'\u25c6':
                post_file.write(content.encode('utf-8'))
                print content.encode('utf-8')
        for push in post.find_all('div', 'push'):
          print push.contents[2].contents[0].encode('utf-8')
          post_file.write(push.contents[1].contents[0].encode('utf-8') + push.contents[2].contents[0].encode('utf-8'))

        post_file.close()

        ## delay for a little while in fear of getting blocked
        time.sleep(0.1)

## dump the number of pushes mapping to the file 'num_pushes_json'
num_pushes_file = open('num_pushes_json', 'w')
json.dump(num_pushes, num_pushes_file)




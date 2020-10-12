import requests # for web requests
from bs4 import BeautifulSoup # a powerful HTML parser
from selenium.webdriver import Chrome
import pandas as pd # for .csv file read and write
import re # for regular regression handling
#from requests_html import HTMLSession
#session = HTMLSession()

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
path = "/usr/local/Caskroom/chromedriver/86.0.4240.22/chromedriver"
driver = Chrome(executable_path=path)
driver.implicitly_wait(3)

""" get all position <a> tags for the list of articles, results stored in a dictionary"""
def linksByKeys(keys):
    ## keys: a list of article keywords
    ## return: a dictionary of links

    links_dic = dict()
    # scrape key words one by one
    for key in keys:
        print('Scraping articles: ', key, ' ...')
        links_dic[key] = linksByKey(key)
        print('{} {} articles found!'.format(len(links_dic[key]),key))
    return links_dic


""" get all position <a> tags for a single article, triggered by linksByKeys function """
def linksByKey(key):
    ## key: search keyword
    ## return: a list of links

    # parameters passed to  http get/post function
    base_url = 'https://www.thestar.com.my/search/'
    params = {'q':'','QDR':'QDR_simple','DateRange_DDL' : 'anytime', 'QDR' : 'QDR_simple','qsort' : 'newest', 'qrec':30,'pgno': None}
    params['q'] = key

    # page number
    pn = 1

    position_links = []
    loaded = True
    while loaded:
        print('Loading page {} ...'.format(pn))
        params['pgno'] = pn
        r = requests.get(base_url, headers=headers, params=params)

        # extract position <a> tags
        soup = BeautifulSoup(r.text,'html.parser')
        links = soup.find_all('a',{'data-content-type':'Article'})

        # if return nothing, means the function reach the last page, return results
        if not len(links):
            loaded = False
        else:
            position_links += links
            pn += 1
    return position_links


""" parse HTML strings for the list of roles"""
def parseLinks(links_dic):
    ## links_dic: a dictionary of links
    ## return: print parsed results to .csv file

    for key in links_dic:
        jobs = []
        for link in links_dic[key]:
            jobs.append([key] + parseLink(link))

        # transfrom the result to a pandas.DataFrame
        result = pd.DataFrame(jobs,columns=['key_word','article_id','title','category','author','article_href','content','side_note'])

        # save result,
        file_name = key+'.csv'
        result.to_csv(file_name,index=False)


""" parse a single <a> tag, extract the information, triggered by parseLinks function """
def parseLink(link):
	## link: a single position <a> tag
	## return: information of a single article

	# unique id assigned to an article
	article_id = link['data-content-id'].strip()
	# article title
	title = link['data-content-title'].strip()
	# posted country
	category = link['data-content-category'].strip()
	# the web address towards to the post detail page
	author = link['data-content-author'].strip()
	# the web address towards to the post detail page
	article_href = link['href']
	# go to post detail page, and fetch information
	other_detail = getArticleDetail(article_href)

	return [article_id,title,category,author, article_href] + other_detail


""" extract details from post detail page """
def getArticleDetail(article_href):
    ## article_href: an article url
    ## return: post details from the article page

    print('Scraping ',article_href,'...')
    driver.get(article_href)
	
    try:
        content=driver.find_element_by_id("story-body").text
    except:
        content = None
    try:
        side_note=driver.find_element_by_id("sideNote").text
    except:
        side_note = None
    
    return [content, side_note]

def main():

    # a list of key words to be crawled
    key_words = ['wall street crash']
    s = requests.session()
    links_dic = linksByKeys(key_words)
    parseLinks(links_dic)

if __name__ == '__main__':
	main()

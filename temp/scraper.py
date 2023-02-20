import re
from urllib.parse import urlparse
from lxml import etree
from io import StringIO
import urllib.robotparser
from bs4 import BeautifulSoup

#check sli.ics.edu links. nothing seems to be working

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []

    
    #print("This is the url")
    #print(url)
    domain = "ics.uci.edu"

    sliHandler = "sli.ics.uci.edu"
    commentHandler = '#comment'
    respondHandler = '#respond'
    actionHandler = "action="
    
    if(resp.status==200):  
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')  
        for link in soup.find_all('a'):
            #print(link.get('href'))

            #Handle comments
            if(domain not in str(link.get('href'))):
                continue

            if(sliHandler in str(link.get('href'))):
                continue
                
            if((commentHandler not in str(link.get('href'))) and (respondHandler not in str(link.get('href'))) and (actionHandler not in str(link.get('href')))):
                links.append(link.get('href'))

        #print("found " + str(len(links)) + " links")
  
    if(resp.status>=600):
        print("the error is ")
        print(resp.error)
        print()
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        
        parsed = urlparse(url)
        domain = "ics.uci.edu"
        if parsed.scheme not in set(["http", "https"]):
            return False

        #Allow only urls with "ics.uci.edu" domain
        '''Can definitely improve this'''
        if(domain not in url):
            return False

        #consider removing .odc and .sql as well?
        #We need to handle comments. Different comments point to the same site.
        #maybe look for '#comment- ' what about .php?
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|r|m|py|sql|bib|java|ss|scm|php|zip)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

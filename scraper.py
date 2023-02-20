import re

from urllib.parse import urlparse

from lxml import etree

from io import StringIO

import urllib.robotparser

from bs4 import BeautifulSoup

import html.parser


def getDictWords():

    dict_f = {}

    f = open("./results/wordDictionaryData.txt", "r")

    raw = f.readline()

    while len(raw) > 0:

        try:

            data = raw.replace("\n", "").replace("\r", "").split(" ");

            dict_f[data[0]] = data[1]

        except:

            error = ""

        raw = f.readline()

    f.close()

    return dict_f


def getListURLs():

    list_f = list()

    f = open("./results/listURLData.txt", "r")

    raw = f.readline()

    while len(raw) > 0:

        try:

            data = raw.replace("\n", "").replace("\r", "")

            list_f.append(data)

        except:

            error = ""

        raw = f.readline()

    f.close()

    return list_f


def getStopWords():

    list_stopword = list();

    with open("./stopword.txt", "r") as file: 

        str_stopwords = file.readline()

        while len(str_stopwords) > 0:

            try:

                str_stopwords = re.sub('[^0-9a-zA-Z]+', '', str_stopwords)

                list_stopword.append(str_stopwords)

            except:

                error = ""

            str_stopwords = file.readline()

    return list_stopword


def writeResultUrlToFile(list_url, dict_url):

    with open("./results/resultUniqueURLData.txt", "w") as file: 

        for url in list_url:

            file.write(url + "\n")

    with open("./results/resultICSUniqueURLData.txt", "w") as file: 

        for url in dict_url:

            file.write(url + " " + str(dict_url[url]) + "\n")

        print("Result Data successfully written")

    return


def writeResultWordDictToFile(wordDictionary):
    list_stop = getStopWords()
    with open("./results/resulttop50wordData.txt", "w") as file: 

        int_count = 0

        for word in wordDictionary:
            if word in list_stop:
                
                continue
            
            if int_count == 50:
                
                break

            file.write(word + " " + str(wordDictionary[word]) + "\n")

            int_count += 1

        print("Result Data successfully written")

    return

'''

just put some space here to mark new stuff

'''


def outputfilteredResult():
    list_uniqueUrl = list()
    dict_icsUrl = {}
    dict_words = getDictWords()
    list_urls = getListURLs()
    for url in list_urls:
        url = url.replace("https://", "").replace("http://", "").lower()
        unique = url.split("/")[0]
        if not unique in list_uniqueUrl:
            list_uniqueUrl.append(unique)
        if "ics.uci.edu" in unique:
            if unique in dict_icsUrl.keys():
                dict_icsUrl[unique] = dict_icsUrl[unique] + 1
            else:
                dict_icsUrl[unique] = 1
    sorted_dict_icsUrl = dict(sorted(dict_icsUrl.items(), key=lambda x:x[0], reverse=False))
    writeResultUrlToFile(list_uniqueUrl, sorted_dict_icsUrl)
    
    sorted_dict_words = dict(sorted(dict_words.items(), key=lambda x:int(x[1]), reverse=True))
    writeResultWordDictToFile(sorted_dict_words)


def writeDictToFile(wordDictionary):

    with open("./results/wordDictionaryData.txt", "w") as file: 

        for word in wordDictionary:

            file.write(word + " " + str(wordDictionary[word]) + "\n")

        print("Data successfully written")

    return


def writediscardedListToFile(urlList):

    with open("./results/discarderdData.txt", "a+") as file: 

        for url in urlList:

            file.write(url + "\n")

        print("Data successfully written")

    return


def writeListToFile(urlList):

    with open("./results/listURLData.txt", "a+") as file: 

        for url in urlList:

            file.write(url + "\n")

        print("successfully written")

    return


def scraper(url, resp):

    # get info

    list_raw = list()

    int_count = 0

    dict_words = {}

    if (resp.status == 200):

        b_raw = resp.raw_response.content
        soup = BeautifulSoup(b_raw,features="lxml")
        alltxtcontent = soup.text

        words = re.split("\s", re.sub("[^a-z 0-9 ' - ]", ' ', alltxtcontent.lower()))
 
        for word in words:
            if(word.isnumeric()  or len(word)<=1):
                continue

            int_count += 1
            if not (word in dict_words.keys()):
                dict_words[word] = 1
            else:
                dict_words[word] += 1


    links = extract_next_links(url, resp)

    consideredLinks = []
    discardedLinks = []
    
    for link in links:
        if (is_valid(link)):
            consideredLinks.append(link)
        else:
            discardedLinks.append(link)

    return consideredLinks, int_count, dict_words, discardedLinks





def checkNeed(str_url):

    # TRUE = SKIP

    # FALSE = will be searched

    

    DateRegex = re.compile(r'\d\d\d\d-\d\d')

    DateRegex1 = re.compile(r'\d\d\d\d/\d\d')

    PageRegex = re.compile(r'(page/)(\d)')

    PageRegex1 = re.compile(r'(pages/)(\d)')

    PageRegex2 = re.compile(r'(p=)(\d)')

    tagRegex = re.compile(r'tags/\d')

    commentRegex = re.compile(r'comment-\d')

    postRegex = re.compile(r'posts/\d')

    bibRegex = re.compile(r'\d.bib')

    dr = DateRegex.search(str_url)

    dr1 = DateRegex1.search(str_url)

    pr = PageRegex.search(str_url)

    pr1 = PageRegex1.search(str_url)

    pr2 = PageRegex2.search(str_url)

    pstr = postRegex.search(str_url)

    cmtr = commentRegex.search(str_url)

    bibr = bibRegex.search(str_url)

    tr = tagRegex.search(str_url)

    sliHandler = "sli.ics.uci.edu"

    commentHandler = '#comment'

    respondHandler = '#respond'

    actionHandler = "action="

    shareHandler = "share="

    refreshHandler = "refresh="


    
    if(sliHandler in str_url or (shareHandler in str_url)):
        return True


    if(commentHandler not in str_url and (respondHandler not in str_url) and (actionHandler not in str_url)):
        return False


    if(dr or dr1 or pstr or cmtr or bibr or tr):

        return True

    if(pr):

        if(pr.group(1) == "1"):

            return False

        return True

    if(pr1):

        if(pr1.group(1) == "1"):

            return False

        return True

    if(pr2):

        if(pr2.group(1) == "1"):

            return False

        return True

    

    return False





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

    

    # print("This is the url")

    # print(url)

    domain = "ics.uci.edu"

    domain1 = "wics.uci.edu"



    if(resp.status == 200): 

        soup = BeautifulSoup(resp.raw_response.content, 'lxml')  

        for link in soup.find_all('a'):

            # print(link.get('href'))



            # Handle comments

            # if(domain not in str(link.get('href'))):

            #    continue




            if(not checkNeed(str(link.get('href')))):
                links.append(str(link.get('href')))


        # print("found " + str(len(links)) + " links")

  

    if(resp.status >= 600):
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

        str_hostname = str(parsed.hostname)

        if "ics.uci.edu" not in str_hostname and "stat.uci.edu" not in str_hostname and "cs.uci.edu" not in str_hostname and "informatics.uci.edu" not in str_hostname and "today.uci.edu/department/information_computer_sciences/" not in str_hostname:

            return False

        if parsed.scheme not in set(["http", "https"]):

            return False

        return not re.match(

            r".*\.(css|js|bmp|gif|jpe?g|ico"

            +r"|png|tiff?|mid|mp2|mp3|mp4"

            +r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"

            +r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"

            +r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"

            +r"|epub|dll|cnf|tgz|sha1"

            +r"|thmx|mso|arff|rtf|jar|csv"

            +r"|rm|smil|wmv|swf|wma|zip|rar|gz|r|m|py|sql|bib|java|ss|scm|ppsx|zip)$", parsed.path.lower())

    except TypeError:

        print ("TypeError for ", parsed)

        raise


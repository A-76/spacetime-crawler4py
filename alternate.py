import re
import html.parser
from urllib.parse import urlparse

searched_url = {};  # this is for the checking if pages are from same URL 
# (the part after '/' are removed)
# for step in the assignment 2, I looped through this dict and get the url contains ics uci, 
# there are some url have different ports, I still see them as different URL

searched_list_url = list();  # this is all of the URL that has been searched
dict_words = {}  # for counting words
int_max = 0  # the max num of words in a page


class siteData

def readWordFile():
    return readDictFromFile("dictWordData.txt")


def writeWordFile(dict_f):
    writeDictToFile("dictWordData.txt", dict_f)


def readDataFile():
    return readDictFromFile("Data.txt")


def writeDataFile(dict_f):
    writeDictToFile("Data.txt", dict_f)

    
def readURLDFile():
    return readDictFromFile("dictURLData.txt")


def writeURLDFile(dict_f):
    writeDictToFile("dictURLData.txt", dict_f)

   
def readURLLFile():
    return readListFromFile("listURLData.txt")


def writeURLLFile(list_f):
    writeListToFile("listURLData.txt", dict_f) 

    
def readListFromFile(f_name):
    list_f = list();
    check_file = os.path.isfile(f_name)
    if not(check_file):
        return dict_f
    f = open(f_name, "r")
    raw = f.readline()
    while(raw):
        data = raw.remove("\n", "").remove("\r", "");
        list_f.append(data)
        raw = f.readline()
    f.close()
    return list_f


def writeListToFile(f_name, dict_f):
    f = open(f_name, "w+")
    for data in dict_f():
        f.write(data + "\r\n")
    f.close()


def readDictFromFile(f_name):
    dict_f = {}
    check_file = os.path.isfile(f_name)
    if not(check_file):
        return dict_f
    f = open(f_name, "r")
    raw = f.readline()
    while(raw):
        data = raw.remove("\n", "").remove("\r", "").split(" ");
        dict_f[data[0]] = data[1]
        raw = f.readline()
    f.close()
    return dict_f


def writeDictToFile(f_name, dict_f):
    f = open(f_name, "w+")
    for data in dict_f.keys():
        f.write(data + " " + dict_f[data] + "\r\n")
    f.close()



def scraper(url, resp):
    # get info
    global searched_url
    global int_max
    list_raw = list();
    int_count = 0
    if (resp.status == 200):
        global dict_words
        b_raw = resp.raw_response.content
        raw = ""
        try:
            raw = b_raw.decode('utf-8')
        except:
            raw = str(b_raw)
        try:
            raw = html.unescape(raw).replace("%09", " ").replace("\n", " ")
        except:
            return
        bool_read = True
        str_word = ""
        html_stack = list();
        bool_comment = False
        for c in raw:
            if(c == '<' and bool_read):
                if(len(str_word) > 0 and not bool_comment):
                    list_raw.append(str_word)
                str_word = ""
                bool_read = False
                continue
            if(c == '>' and not bool_read):
                if(str_word.endswith("--")):
                    bool_comment = False
                    str_word = ""
                    continue
                bool_read = True
                if(str_word.startswith("/")):
                    str_word = ""
                    if(html_stack):
                        html_stack.pop()
                    continue
                if not(bool_comment):
                    html_stack.append(str_word)
                str_word = ""
                continue
            str_type = ""
            if(html_stack):
                str_type = html_stack[-1]
            if bool_read and not str_type.startswith("/")  and not (str_type.startswith("a ") or str_type == "a" or "span" in str_type or str_type == "p" or str_type == "br" or str_type == "b" or str_type == "i" or str_type == "q" or str_type.startswith("h") or str_type.startswith("p style")):
                continue
            str_word += c
            if(str_word == "!--" and not bool_read):
                bool_comment = True
                str_word = ""
                
    for rawline in list_raw:
        list_replaced = rawline.replace(chr(9), "").replace("=", "").replace(">", "").replace("<", "").replace("*", "").replace("?", "").replace(";", "").replace(":", "").replace("!", "").replace("/", " ").replace("“", "").replace("”", "").replace("-", "").replace(",", "").replace("(", "").replace(")", "").replace(".", "").replace("[", "").replace("]", "").replace("&", "").replace("\"", "").split(" ")
        for word in list_replaced:
            word = word.replace(" ", "");
            if(word == " " or len(word) <= 1 and not (word == "i" or word == "a")):
                continue
            int_count += 1
            if not (word in dict_words.keys()):
                dict_words[word] = 1
            else:
                dict_words[word] += 1

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)],int_count,dict_words


def checkNeed(str_url):
    # TRUE = SKIP
    # FALSE = will be searched
    
    sliHandler = "sli.ics.uci.edu"
    commentHandler = '#comment'
    respondHandler = '#respond'
    actionHandler = "action="
    # check for url about ics.uci are in the is_valid function, see line 284
    
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
                links.append(str(ink.get('href')))

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
        str_hostname = str(parsed.hostname)
        if "ics.uci.edu" not in str_hostname and "stat.uci.edu" not in str_hostname and "cs.uci.edu" not in str_hostname and "informatics.uci.edu" not in str_hostname and "today.uci.edu/department/information_computer_sciences/" not in str_hostname:
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
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

from threading import Thread
import sys
from inspect import getsource
from utils.download import download
from utils import get_logger
import urllib.robotparser
import scraper
import time
import socket
socket.setdefaulttimeout(25)

#Write a functon for subdomains as well number of unique ones
class Worker(Thread):
 
    def __init__(self, worker_id, config, frontier,lock,site_tracking,total_scraped_urls,wordDictionary,allThreadStatus):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.lock = lock
        self.id1 = worker_id
        self.site_tracking = site_tracking
        

        #Below is overall statistics that are required 
        self.total_scraped_urls = total_scraped_urls
        self.intMax = 0
        self.wordDictionary = wordDictionary
        self.threshold = 5000
        self.allThreadStatus = allThreadStatus #This variable is used to check if all the threads have completed execution. the thread incrememts this variable when it completes and the last thread writes to file.
        self.numThreads = config.threads_count

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            
            tbd_url = self.frontier.get_tbd_url()

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                self.lock.acquire()
                self.allThreadStatus.append(1)
                print("The value of allthreads is " +str(len(self.allThreadStatus)))
                print("The value of allthreads is " +str(self.numThreads))
                if(len(self.allThreadStatus)==self.numThreads):
                        scraper.writeListToFile(self.total_scraped_urls)
                        scraper.writeDictToFile(self.wordDictionary)
                        scraper.outputfilteredResult()
                        self.total_scraped_urls.clear()
                    
                        print("written all data to files")
                self.lock.release()
                break

            #print(str(self.id1) + " " + tbd_url)
            http0 = "http://"
            https1  = "https://"
            '''
            self.lock.acquire()
            self.allThreadStatus.append(1)
            
            print("The length is " + str(len(self.allThreadStatus)))
            print(self.allThreadStatus)
            if(len(self.allThreadStatus)==3):
            	print("Good Work")
            	self.allThreadStatus.clear()
            self.lock.release()
            '''
            a = False
            if(http0 in tbd_url):
                a= True
                rawurl = tbd_url.replace(http0, "")
            elif(https1 in tbd_url):
                a= False
                rawurl = tbd_url.replace(https1, "")
            else:
                continue

            str_url = ""
            for c in rawurl:
                if c == "/":
                    break
                str_url += c
                
            #print(str_url)
            possible_domains = ["stat.uci.edu","ics.uci.edu","informatics.uci.edu","cs.uci.edu"]
            x = {}
            #x["www.stat.uci.edu"] = 12
            #x["www.ics.uci.edu"] = 11
            #x["www.informatics.uci.edu"] = 19
            #x["www.cs.uci.edu"] = 10

            #print(str_url)
            flag = False
            for domain in possible_domains:
                if(str_url.find(domain)):
                    flag=True
                    if(not a):
                        robotsTXT = https1 + str_url + "/robots.txt"
                    else:
                        robotsTXT = http0 + str_url + "/robots.txt"
                    break

            if(flag):
                #print(robotsTXT)
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(robotsTXT)
                site = ''
                
                try:

                    rp.read()
                    #if(self.id1==1):
                    #    print("thread " + str(self.id1))
                    #print("cool")
                    delay = rp.crawl_delay("*")
                    #print("the delay is")
                    #print(delay)
                    if(delay is not None): 
                        if(a):
                            site = tbd_url[6:loc+x[domain]]
                        else:
                            site = tbd_url[7:loc+x[domain]]

                        #print("this is the site")
                        #print(site)
                        self.lock.acquire()
                        if(site in self.site_tracking.keys()):
                            if(time.time() - self.site_tracking[site] <= delay):
                                #self.site_tracking[site] = time.time()
                                self.frontier.add_url(tbd_url)
                                continue
                            else:
                                self.site_tracking[site] = time.time()
                        self.lock.release()
                    #print("cool")
                    if(rp.can_fetch("*", tbd_url)):
                        #if the robots.txt file has a sitemap 
                        possible_sites = rp.site_maps()
                        if(possible_sites is not None):
                            for site in possible_sites:
                                #print("Added a site from site map")
                                #print(site)
                                self.frontier.add_url(site)

                        resp = download(tbd_url, self.config, self.logger)
                        scraped_urls,wordCount,wordDictionary,discardedLinks = scraper.scraper(tbd_url, resp)

                        if(wordCount>self.intMax):
                            self.intMax = wordCount

                        self.lock.acquire()
                        self.total_scraped_urls.append(tbd_url)

                        self.logger.info(
                            f"Downloaded {tbd_url}, status <{resp.status}>, "
                            f"using cache {self.config.cache_server}.")

                        for word in wordDictionary:
                            if(word in self.wordDictionary):
                                self.wordDictionary[word] += wordDictionary[word]
                            else:
                                self.wordDictionary[word] = wordDictionary[word]
                        
                        if(self.id1==0):
                            if(len(self.wordDictionary.keys()) >self.threshold):
                                scraper.writeListToFile(self.total_scraped_urls)
                                scraper.writeDictToFile(self.wordDictionary)
                                self.threshold = len(self.wordDictionary.keys()) + 10000
                                self.total_scraped_urls.clear()
                            print("currently there are " + str(len(self.total_scraped_urls) )+ " number of urls.")
                            print("The current frontier size is " + str(self.frontier.frontier_get_size()))
                            print("currently there are " + str(len(self.wordDictionary.keys()) )+ " number of unique words and the threshold is " + str(self.threshold)) 
                            print()
                    
                        scraper.writediscardedListToFile(discardedLinks)
                        for scraped_url in scraped_urls:
                            self.frontier.add_url(scraped_url)
                        self.frontier.mark_url_complete(tbd_url)
                        self.lock.release()
                        time.sleep(self.config.time_delay)
                    
                except Exception as e:
                    #Store the site in a log
                    print("This is thread "+ str(self.id1))
                    print("failed to connect to below ")
                    print(tbd_url)
                    with open("./fail_to_connect.txt","a+") as file:
                        file.write(str(tbd_url))
                        file.write("\n")
                        file.write(str(e))
                        file.write("\n")
                        file.write(str(self.id1))
                        file.write("\n")
                        file.write("\n")


        

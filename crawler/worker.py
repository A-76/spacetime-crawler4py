from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import urllib.robotparser
import scraper
import time


class Worker(Thread):

    site_tracking = {}    
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            #print(tbd_url)
            possible_domains = ["stat.uci.edu","ics.uci.edu","informatics.uci.edu","cs.uci.edu"]
            x = {}
            x["stat.uci.edu"] = 12
            x["ics.uci.edu"] = 11
            x["informatics.uci.edu"] = 19
            x["cs.uci.edu"] = 10

            flag = False
            for domain in possible_domains:
                loc = str(tbd_url).find(domain)
                if(loc!= -1):
                    robotsTXT = tbd_url[:loc+x[domain]] + "/robots.txt"
                    flag = True
                    break

            if(flag):
                #print(robotsTXT)
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(robotsTXT)
                site = ''
                try:
                    rp.read()
                    delay = rp.crawl_delay("*")
                    #print("the delay is")
                    #print(delay)
                    if(delay is not None):
                        start_pos1 = "http://"
                        start_pos2 = "https://"

                        loc = str(tbd_url).find(start_pos1)
                        
                        if(loc != -1):
                            site = tbd_url[6:loc+x[domain]]
                        else:
                            site = tbd_url[7:loc+x[domain]]

                        print("this is the site")
                        print(site)
                        if(site in self.site_tracking.keys()):
                            if(time.time() - self.site_tracking[site] <= delay):
                                self.site_tracking[site] = time.time()
                                self.frontier.add_url(tbd_url)
                                continue

                        self.site_tracking[site] = time.time()

                    if(rp.can_fetch("*", tbd_url)):
                        #if the robots.txt file has a sitemap 
                        possible_sites = rp.site_maps()
                        if(possible_sites is not None):
                            for site in possible_sites:
                                print("Added a site from site map")
                                print(site)
                                self.frontier.add_url(site)

                        resp = download(tbd_url, self.config, self.logger)
                        self.logger.info(
                            f"Downloaded {tbd_url}, status <{resp.status}>, "
                            f"using cache {self.config.cache_server}.")
                        scraped_urls = scraper.scraper(tbd_url, resp)
                        for scraped_url in scraped_urls:
                            self.frontier.add_url(scraped_url)
                        self.frontier.mark_url_complete(tbd_url)
                        time.sleep(self.config.time_delay)

                except Exception as e:
                    #Store the site in a log
                    print("failed to connect")
                    print(tbd_url)
                    with open("./fail_to_connect.txt","a+") as file:
                        file.write(str(tbd_url))
                        file.write("\n")
                        file.write(str(e))
                        file.write("\n")
                        file.write("\n")



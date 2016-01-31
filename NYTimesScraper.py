from bs4 import BeautifulSoup
from selenium import webdriver
import time,re

BASE = "http://query.nytimes.com/search/sitesearch/#/*/since1851/allresults/{num}/allauthors/oldest/"

def cleanUp(junk):
    if not junk:
        return None
    x = str(junk.get_text()).encode('ascii','ignore')
    return re.sub('\n|\t/|\r',' ',x).strip()
        
def getSource(url,br, sleep = 0.2):
    br.get(url)
    time.sleep(sleep)
    src = br.page_source.encode('ascii','ignore')
    return src


def seleniumScrape():
    br = webdriver.PhantomJS()
    f = open('nytimesarticles.txt','w')
    i = 1
    t = 0.5
    while True:
        src = getSource(BASE.format(num = str(i)),br,sleep = t)
        soup = BeautifulSoup(src,"html.parser")
        del src
        IN = False
        try:
            for li in soup.find_all('li',{"class": "story"}):
                IN = True
                summary = cleanUp(li.find("p",{"class":"summary"}))
                div = li.find("div",{"class":"storyMeta"})
                date = cleanUp(div.find("span",{"class":"dateline"}))
                author = cleanUp(div.find("span",{"class":"byline"}))
                author = re.sub('By ','',author)
                section = cleanUp(div.find("span",{"class":"section"}))
                headline = cleanUp(div.find("span",{"class":"printHeadline"}))
                headline = re.sub('Print Headline: ','',headline)
                href = str(li.find('a').get('href'))
                line = []
                for datum in [headline,date,href,summary,section,author]:
                    if datum:
                        line.append(datum)
                    else:
                        line.append("NA")
                if line:
                    f.write('|'.join(line) + '\n')
#                 print line
            print i,i/15191793.0,t
            if IN:
                i += 1000
                t = 0.5
            else:
                t += 0.1
            if t >= 10:
                break
#             if i%10 == 0:
#                 br.quit()
#                 br = webdriver.PhantomJS()
        except Exception as e:
            print "ERROR at ",i,':',e
        del soup
    f.close()
    

if __name__ == "__main__":
    seleniumScrape()

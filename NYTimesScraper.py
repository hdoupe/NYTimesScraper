from bs4 import BeautifulSoup
from selenium import webdriver
import time,re

BASE = "http://query.nytimes.com/search/sitesearch/#/*/from{date}to20160101/allresults/{page}/allauthors/oldest/"
START = 'January 01, 1851'
STOP = 'January 01, 2016'

dates = {'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06',
	'July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}

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

def formatDate(date):
	date = re.split("\ |,",date)
	date = [str(d) for d in date if d]
	return ''.join([date[2],dates[date[0]],date[1]])


def seleniumScrape():
	br = webdriver.PhantomJS()
	f = open('nytimesarticles.txt','w')
	t = 0.5
	date = formatDate(START)
	stopDate = formatDate(STOP)
	articleDate = ""
	while date != stopDate:
		for page in range(1,100):
			try:
				src = getSource(BASE.format(date = date, page = page),br,sleep = t)
				soup = BeautifulSoup(src,"html.parser")
				del src
				for li in soup.find_all('li',{"class": "story"}):
					IN = True
					summary = cleanUp(li.find("p",{"class":"summary"}))
					div = li.find("div",{"class":"storyMeta"})
					articleDate = cleanUp(div.find("span",{"class":"dateline"}))
					author = cleanUp(div.find("span",{"class":"byline"}))
					author = re.sub('By ','',author)
					section = cleanUp(div.find("span",{"class":"section"}))
					headline = cleanUp(div.find("span",{"class":"printHeadline"}))
					headline = re.sub('Print Headline: ','',headline)
					href = str(li.find('a').get('href'))
					line = []
					for datum in [headline,articleDate,href,summary,section,author]:
						if datum:
							line.append(datum)
						else:
							line.append("NA")
					if line:
						f.write('|'.join(line) + '\n')
		#                 print line
				del soup
			
				if page == 99:
					date = formatDate(articleDate)
					print date,articleDate
			except Exception as e:
				print date,e
	f.close()


if __name__ == "__main__":
	seleniumScrape()

import scrapy
from scrapy.http import Request
import json

#this method allows me to extract all the href tags in the html body, XPath for each element is needed to do so.
def extractLink(s,baseURL):
    temp=[]
    for i in s.split():
        if('href' in i):
            if('.pdf' in i):
                a=i.replace('href="',"")
                a=a.replace('"',"")
                a=a.split(">")[0]
                '''if("../" in a):
                    a=a.replace("../",baseURL)
                elif("./" in a):
                    a=a.replace("./",baseURL)'''
                temp.append(a)
    return temp

class pdf_scraper(scrapy.Spider):
    name="pdf"
    allowed_urls=["https://www.privacy.gov.ph/"]
    start_urls=["https://www.privacy.gov.ph/data-privacy-act-primer/","https://www.privacy.gov.ph/memorandum-circulars/","https://www.privacy.gov.ph/advisories/","https://www.privacy.gov.ph/advisory-opinions/","https://www.privacy.gov.ph/commission-issued-orders/"]
    #start_urls=["https://www.privacy.gov.ph/data-privacy-act-primer/"]
    
    def __init__(self):
        self.metadata=[]

    def parse(self,response):
        self.logger.info("This is running")
        sel=scrapy.Selector(response)
        link=sel.xpath('/html/body').get()
        for download_url in extractLink(link,"https://www.privacy.gov.ph/"): 
            try:
                yield Request(
                    url=download_url,
                    callback=self.save_pdf
                )
            except:
                #this handels repetion and error in URLs I hace tried to getv all the possible pdfs on the different pages.
                pass

    def save_pdf(self, response):
        path = response.url.split('/')[-1]
        temp={}
        temp['name']=path
        temp['content-type']=str(response.headers['Content-Type'])
        temp['date']=str(response.headers['Last-Modified'])
        temp['response_url']=(response.url)
        path = "downloads/"+path
        temp['file_path']=path
        self.metadata.append(temp)
        self.logger.info('Saving PDF %s', path)
        with open(path, 'wb') as f:
            f.write(response.body)
        with open('metadata.json','w') as d:
            d.write(json.dumps(self.metadata))

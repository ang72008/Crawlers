#encoding:utf-8
import scrapy
import time
from selenium import webdriver
import MySQLdb
from scrapy.selector import Selector
from items import cnkiItem

class autInfoSpider(scrapy.Spider):
    name = "autinfocnkinew"
    start_urls = ["http://kns.cnki.net/kns/brief/result.aspx"]
    
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.autInfoConn = MySQLdb.connect(host='localhost', port = 3306, user='xx', passwd='xx', db ='xx')
        self.autInfoConn.set_character_set('utf8')
        self.autInfoCur = self.autInfoConn.cursor()
        self.autInfoCur.execute("select autid,name,org from speclst where finishflag=0")
        self.autRecords = self.autInfoCur.fetchall()
        self.autcnt = 0
        self.insertcnt = 0
        self.finishcnt = 0
        self.viewflagcnt = 0
        self.errcounter = 0
        self.urllist = []
    #文本中引号处理            
    def filterStr(self,string):
        newStr = ''
        for eachChar in string:
            if eachChar == '"':
                newStr += '"'
                newStr += '"'
            elif eachChar =="'":
                newStr +="'"
                newStr += "'"
            elif eachChar == '\\':
                pass
            else:
                newStr += eachChar
        return newStr
    #reset高级检索页面，发送检索信息（作者和其所在机构），获取iframe地址
    def sendkeys(self,idrec,autrec,orgrec):
        starturl = "http://kns.cnki.net/kns/brief/result.aspx"
        self.browser.get(starturl)
        try:
            self.browser.maximize_window()
        except Exception,e:
            print e
        time.sleep(3)
        aut = autrec.decode('utf-8')
        org = orgrec.decode('utf-8')
        print "aut=%s,org=%s" %(aut,org)
        self.autcnt += 1
        print "%d author(s) processed" %self.autcnt
        authorinputbox = self.browser.find_element_by_id('au_1_value1')
        orginputbox = self.browser.find_element_by_id('au_1_value2')
        authorinputbox.clear()
        authorinputbox.send_keys(aut)
        orginputbox.clear()
        orginputbox.send_keys(org)
        '''try:
            qrclosebt = self.browser.find_element_by_xpath('//div[@id="fixedbox1"]/a')
            qrclosebt.click()
            time.sleep(1)
        except Exception, e:
            print e'''
        try:
            clearbtn = self.browser.find_element_by_xpath('//div[@id="XuekeNavi_Div"]/div[@class="opt"]/input[1]')
            clearbtn.click()
            time.sleep(1)
        except Exception, e:
            print e
        #self.browser.implicitly_wait(3)
        submitbtn = self.browser.find_element_by_id("btnSearch")
        submitbtn.click()
        self.autInfoCur.execute("update speclst set checkflag = 1 where autid=%s"%idrec)
        self.autInfoConn.commit()
        print "This person checked!"
        time.sleep(5)
        iframeurlFrag = Selector(text=self.browser.page_source).xpath('//iframe[@id="iframeResult"]/@src').extract()
        #print "iframeurlFrag=",iframeurlFrag
        iframeurl = "http://kns.cnki.net/kns/brief/" + ''.join(iframeurlFrag) + "&DisplayMode=custommode"
        return self.autcnt,iframeurl
    #跳转50条结果视图，重新获取页面
    def switchView(self):
        try:
            viewpagenum = Selector(text=self.browser.page_source).xpath('//div[@id="id_grid_display_num"]/a[3]/@href').extract()
            iframeurl = "http://kns.cnki.net" + ''.join(viewpagenum)
            self.browser.get(iframeurl)
            self.viewflagcnt += 1
            time.sleep(5)
        except Exception,e:
            print e
            alert = self.browser.switch_to.alert
            time.sleep(3)
            alert.accept()
            self.browser.get('about:blank')
        return self.viewflagcnt,iframeurl
    #获取该作者所有搜索结果页面的跳转链接 和结果数   
    def getUrlList(self,iframeurl,urllist):
        try:
            self.browser.get(iframeurl)
        except Exception,e:
            print e
            alert = self.browser.switch_to.alert
            time.sleep(3)
            alert.accept()
            self.browser.get('about:blank')
        time.sleep(5)
        if self.viewflagcnt < 1:
            viewflagcnt,iframeurl = self.switchView()
        artnumfrag = ''.join(Selector(text=self.browser.page_source).xpath('//div[@class="TitleLeftCell"]/div/text()').extract())
        artnumlist = artnumfrag.split()
        artnum = int(artnumlist[1])
        urllist.append(iframeurl)
        try:
            pagenum = ''.join(Selector(text=self.browser.page_source).xpath('//div[@class="TitleLeftCell"]/a[last()-1]/text()').extract())
            #print "pagenum=",pagenum
            path = '//div[@class="TitleLeftCell"]/a[position()<' + pagenum + ']/@href'
            urlfraglist = Selector(text=self.browser.page_source).xpath(path).extract()
            #print "urlfraglist=",urlfraglist
            for urlfrag in urlfraglist:
                url = "http://kns.cnki.net/kns/brief/brief.aspx" + ''.join(urlfrag)
                urllist.append(url)
        except Exception,e:
            print e
        #print "urllist=",urllist
        return artnum,urllist
    #提取文本
    def extract(self,insertcnt):
        item = cnkiItem()
        item['artinfo'] = Selector(text=self.browser.page_source).xpath('//div[@class="GridContent"]/ul//li')
        #print "artinfosrc=", item['artinfo']
        for eachField in item['artinfo']:
            titlelist = eachField.xpath('.//div[@class="GridTitleDiv"]/h3/a/text()').extract()
            title = self.filterStr(''.join(titlelist).encode('utf-8'))
            #print "title=", title.encode('GB18030')
            authorlist = eachField.xpath('.//div[@class="GridContentDiv"]/div/span[@class="author"]/a/font/text()').extract()
            author = ''.join(authorlist[0]).encode('utf-8')
            #print "author=", author.encode('GB18030')
            orglist = eachField.xpath('.//div[@class="GridContentDiv"]/div/span[2]/font/text()').extract()
            org = ''.join(orglist).encode('utf-8')
            #print "org=", org.encode('GB18030')
            suborgdatlist = eachField.xpath('.//div[@class="GridContentDiv"]/div/span[2]/text()').extract()
            suborgdat = ''.join(suborgdatlist)
            suborg = org + suborgdat.replace(u'\uff0c','').replace(u'\u300a','').replace(u'\u300b','').strip('').encode('utf-8')
            #print "suborg=", suborg.encode('GB18030')'''
            journallist = eachField.xpath('.//div[@class="GridContentDiv"]/div/span[3]/a/text()').extract()
            journal = ''.join(journallist).encode('utf-8')
            #print "journal=", journal.encode('GB18030')
            pubdatlist = eachField.xpath('.//div[@class="GridContentDiv"]/div/span[4]/a/text()').extract()
            pubdat = ''.join(pubdatlist).strip()
            pubdate = pubdat.encode('utf-8')
            #print "pubdate=", pubdate.encode('GB18030')'''
            authorslist = eachField.xpath('.//div[@class="GridContentDiv"]/div/span[@class="author"]//a/text()').extract()
            authors = ';'.join(authorslist).strip().encode('utf-8')
            #print "authors=", authors.encode('GB18030')
            abstractlist = eachField.xpath('.//div[@class="GridContentDiv"]/p/text()').extract()
            abstract = ''.join(abstractlist).encode('utf-8')
            #print "abstract=", abstract.encode('GB18030')
            refercntlist = eachField.xpath('.//div[@class="GridContentDiv"]/div[@class="DetailNum"]/label[1]/a/text()').extract()
            refercnt = ''.join(refercntlist).encode('utf-8')
            #print "refercnt=", refercnt.encode('GB18030')
            dowlcntlist = eachField.xpath('.//div[@class="GridContentDiv"]/div[@class="DetailNum"]/a/text()').extract()
            dowlcnt = ''.join(dowlcntlist).encode('utf-8')
            #print "dowlcnt=", dowlcnt.encode('GB18030')
            pubtimelist = eachField.xpath('.//div[@class="GridContentDiv"]/div[@class="DetailNum"]/label[last()]/text()').extract()
            pubTime = ''.join(pubtimelist).split(u'\uff1a')
            pubtime = pubTime[1].encode('utf-8')
            #print "pubtime=", pubtime.encode('GB18030')
            
            #self.autInfoCur.execute("insert into artinfocnki (aut,title,org,suborg,journal,pubdate) values ('%s','%s','%s','%s','%s','%s')" %(author,title,org,suborg,journal,pubdate))
            #break
            self.autInfoCur.execute("update artinfocnki set authors = '%s',abstract = '%s',refercnt = '%s',dowlcnt = '%s',pubtime = '%s' where journal = '%s' and title = '%s'"%(authors,abstract,refercnt,dowlcnt,pubtime,journal,title))
            self.autInfoConn.commit()
            insertcnt += 1
        return insertcnt

    def parse(self,response):
        urllist = self.urllist
        for eachrec in self.autRecords:
            insertcnt = 0
            try:
                try:
                    iframeurl = self.sendkeys(eachrec[0],eachrec[1],eachrec[2])[1]
                except Exception,e:
                    self.errcounter += 1
                time.sleep(5)
                artnum,urlList = self.getUrlList(iframeurl,urllist)
                for url in urlList:
                    self.browser.get(url)
                    insertcnt = self.extract(insertcnt)
                    time.sleep(10)
                
                self.autInfoCur.execute("update speclst set updatecnt = %d,finishflag = 1 where autid=%s" %(insertcnt,eachrec[0]))
                #self.autInfoCur.execute("update speclst set artnum = %d, insertcnt = %d where autid=%s" %(artnum,insertCnt,eachrec[0]))
                self.finishcnt += 1
                self.autInfoConn.commit()
                print "This person finished!"
            except Exception,e:
                print e
            urllist = []
            if self.errcounter > 10:
                break
            #break
            time.sleep(240)
        print "[STAT INFO]\nNum of Authors = %d\nProcessed Num = %d\nFinished Num = %d"%(len(self.autRecords),self.autcnt,self.finishcnt)    
        self.autInfoCur.close()
        self.browser.quit()
        return
        
         
            

            
        
    
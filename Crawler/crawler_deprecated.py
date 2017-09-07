import json
import urllib
import argparse
import logging
from pyquery import PyQuery
import hashlib
import bisect
import socket
import time

''' 根据输入的网址和深度爬网页
    需要对php网页取得真实的网站地址
    所有网址只保留根目录的地址，子目录不保留
    next:
        并行化
        断点续抓
        结果存储为收藏夹的HTML格式
'''

class Crawler(object):
    def __init__(self, args):
        self._baseURL = args.baseURL
        self._depth = args.depth
        self._currentDepth = 0
        self._hyperLinks = [self._baseURL] # 已经爬出来的网址的根目录列表
        self._rawLinks = [] # 所有爬过网页的原始url列表，保证是已排序的
        self._hashList = [] # 所有爬过网址的Hash值列表，且保证是已排序的
        self._hashMap = {}
        self._head = 0
        self._tail = len(self._hyperLinks)

    def CrawlCurrent(self, baseURL):
        print('Depth:', self._currentDepth, ' CrawlCurrent:', baseURL)
        ''' crawl current page '''
        try:
            d = PyQuery(url = baseURL, parser = 'html')
            d.make_links_absolute()
            currentURLs = d('a').map(lambda i, e: PyQuery(e)('a').attr('href'))
        except Exception as e:
            logging.warning('PyQuery: %s : %s\n\tDepth: %d, url: %s', type(e), e, self._depth, baseURL)
            return

        ''' fetch real link '''
        for url in currentURLs:
            ''' 这里是一个优化，避免重复访问相同的url
                先做MD5哈希，然后存入一个list里面，保证list是排好序的
            '''
            
            m = hashlib.md5()
            m.update(url.encode('utf-8'))
            urlHash = m.hexdigest()

##            ''' HashMap优化 '''
##            if urlHash in self._hashMap.keys():
##                logging.info('Optimization-HashMap: oldURL-> %s; newURL-> %s', self._hashMap[urlHash], url)
##            else:
##                self._hashMap[urlHash] = url
##
##            ''' rawURL优化 '''
##            i = bisect.bisect_left(self._rawLinks, url)
##            if i != len(self._rawLinks) and self._rawLinks[i] == url:
##                logging.info('Optimization-rawURL: %s', url)
##                continue
##            else:
##                self._rawLinks.insert(i, url)

            ''' HashList优化 '''
            i = bisect.bisect_left(self._hashList, urlHash)
            if i != len(self._hashList) and self._hashList[i] == urlHash:
                logging.info('Optimization-HashList: %s', url)
                continue
            else:
                self._hashList.insert(i, urlHash)

            print('Depth:', self._currentDepth, ' --> newURL:', url)
            
            try:
                '''
                参考了js中encodeURI的不编码字符
                escape不编码字符有69个：*，+，-，.，/，@，_，0-9，a-z，A-Z
                encodeURI不编码字符有82个：!，#，$，&，'，(，)，*，+，,，-，.，/，:，;，=，?，@，_，~，0-9，a- z，A-Z
                encodeURIComponent不编码字符有71个：!， '，(，)，*，-，.，_，~，0-9，a-z，A-Z
                '''
                url = urllib.parse.quote(url, safe = '!#$&()*+,-./:;=?@_~\'', encoding = 'utf-8')
                req = urllib.request.Request(url)
                response = urllib.request.urlopen(req)
                newURL = response.geturl()
                response.close()
            except urllib.error.URLError as e:
                logging.warning('Request: URLError: %s\n\tDepth: %d, quote url: %s\n\tbaseURL: %s', e.reason, self._depth, url, baseURL)
                continue
            except Exception as e:
                logging.warning('Request: %s : %s\n\tDepth: %d, quote url: %s\n\tbaseURL: %s', type(e), e, self._depth, url, baseURL)
                continue

            parseList = urllib.parse.urlsplit(newURL)
            host = parseList[0] + '://' + parseList[1]

            ''' append '''
            if host not in self._hyperLinks:
                self._hyperLinks.append(host)
                print(host, file = self._printList)

    def CrawlDeeper(self):
        ''' 一次遍历 '''
        self._currentDepth = self._currentDepth + 1
        for i in range(self._head, self._tail):
            self.CrawlCurrent(self._hyperLinks[i])
        self._head = self._tail
        self._tail = len(self._hyperLinks)

    def Dump2File(self):
        outJson = open('links.json', 'w')
        json.dump(self._hyperLinks, outJson)
        outJson.close()

        ''' 格式化输出 '''
        #tmpList = [urllib.parse.urlsplit(url)[1] + '\n' for url in self._hyperLinks]
        tmpList = [url + '\n' for url in self._hyperLinks]
        outList = open('links', 'w')
        outList.writelines(tmpList)
        outList.close()

    def Start(self):
        self._printList = open('printLinks', 'w')
        
        ''' 按深度爬取 '''
        for i in range(self._depth):
            self.CrawlDeeper()

        self.Dump2File()

        self._printList.close()

def main():
    parser = argparse.ArgumentParser(description = 'A crawler for website') 
    parser.add_argument('-a', type=str, required=True, metavar='WebAddr', dest='baseURL', help='Specify the Website Address')
    parser.add_argument('-d', type=int, default=1, metavar='CrawlDepth', dest='depth', help='Specify the Crawler Depth')
    args = parser.parse_args()

    #baseURL = 'http://www.baidu.com'
    
    logging.basicConfig(filename='crawler.log',
                    format='%(asctime)s -> %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S %p',
                    level=logging.DEBUG)
    logging.info('=================== New Session =====================')

    socket.setdefaulttimeout(30) # 对整个socket层设置超时时间(s)。后续文件中如果再使用到socket，不必再设置
    
    crawler = Crawler(args)
    crawler.Start()

if __name__ == '__main__':
    main()

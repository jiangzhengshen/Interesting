import argparse
import hashlib
import logging
import os
import queue
import socket
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from urllib.error import URLError

from pyquery import PyQuery

''' 根据输入的网址和深度爬网页
    需要对php网页取得真实的网站地址
    next:
        并行化
        断点续抓
        URLCrawler: 结果存储为收藏夹的HTML格式
'''


class Crawler(object):
    def __init__(self, args):
        # log设置
        log_file = 'crawler.log'
        logging.basicConfig(filename=log_file,
                            format='%(asctime)s -> %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %H:%M:%S',
                            level=logging.DEBUG)
        logging.info('\n=================== New Session =====================')

        ''' 对整个socket层设置超时时间(s)。后续文件中如果再使用到socket，不必再设置 '''
        socket.setdefaulttimeout(30)

        ''' 不变的参数以"_"开头 '''
        self._init_urls = args.init_urls.split(";")
        self._depth = args.depth
        self._out_dir = args.out_dir if args.out_dir[-1] in ['/', '\\'] else args.out_dir + '/'

        if not os.path.exists(self._out_dir):
            os.mkdir(self._out_dir)

        self.current_depth = 0
        self.url_queue = queue.Queue()  # 待爬取的url队列，格式(url, depth)
        for url in self._init_urls:
            self.url_queue.put((url, self.current_depth))

        self.cached_urls = {}  # 所有爬过网页的原始url，格式url -> [cnt, depth]

    @staticmethod
    def __get_html(url):
        try:
            return PyQuery(url=url, parser='html')
        except Exception as e:
            logging.warning('PyQuery: %s : %s\n\tURL: %s', type(e), e, url)
            return None

    @staticmethod
    def __get_real_url(raw_url):
        try:
            '''
            参考了js中encodeURI的不编码字符
            escape不编码字符有69个：*，+，-，.，/，@，_，0-9，a-z，A-Z
            encodeURI不编码字符有82个：!，#，$，&，'，(，)，*，+，,，-，.，/，:，;，=，?，@，_，~，0-9，a-z，A-Z
            encodeURIComponent不编码字符有71个：!， '，(，)，*，-，.，_，~，0-9，a-z，A-Z
            '''
            url = quote(raw_url, safe='!#$&()*+,-./:;=?@_~\'', encoding='utf-8')
            req = Request(url)
            response = urlopen(req)
            new_url = response.geturl()
            response.close()
            return new_url
        except URLError as e:
            logging.warning('Request: URLError: %s\n\tRaw URL: %s', e.reason, raw_url)
            return ''
        except Exception as e:
            logging.warning('Request: %s : %s\n\tRaw URL: %s', type(e), e, raw_url)
            return ''

    def __extract_url(self, html_pyquery):
        """ extract all the urls from html, except for the cached urls """
        try:
            html_pyquery.make_links_absolute()
            all_urls = html_pyquery('a').map(lambda i, element: PyQuery(element)('a').attr('href'))
            url_list = set()
            for url in all_urls:
                real_url = self.__get_real_url(url)
                if not real_url:
                    continue
                if real_url in self.cached_urls:
                    self.cached_urls[real_url][0] += 1
                else:
                    url_list.add(real_url)
            return list(url_list)
        except Exception as e:
            logging.warning('PyQuery: %s : %s', type(e), e)
            return []

    def __dump_cached_urls(self):
        with open('cached_urls.txt', 'w') as dump_file:
            for url in self.cached_urls:
                dump_file.write(
                    url + '\t' + str(self.cached_urls[url][0]) + '\t' + str(self.cached_urls[url][1]) + '\n')

    @staticmethod
    def filter_url(urls):
        """ could be personalized implemented """
        return urls

    def save_content(self, url, depth, html_pyquery):
        """ could be personalized implemented """
        pass

    def run(self):
        while not self.url_queue.empty() and self.current_depth <= self._depth:
            url_info = self.url_queue.get()
            url = url_info[0]
            depth = url_info[1]
            self.current_depth = depth
            logging.info('Depth: %d, URL: %s', depth, url)

            ''' get html content from the url '''
            html_pyquery = self.__get_html(url)
            if not html_pyquery:
                continue

            ''' save the needed information from the html content, e.g., images, href, etc. '''
            self.save_content(url, depth, html_pyquery)

            ''' cache the crawled urls '''
            if url in self.cached_urls:
                logging.warning('URL: %s -> There should not be cached urls in the queue, check your code !!!', url)
                break
            else:
                self.cached_urls[url] = [1, depth]

            ''' extract urls from the html content, except for the cached urls '''
            extracted_urls = []
            if self.current_depth < self._depth:
                extracted_urls = self.__extract_url(html_pyquery)

            ''' only retain the needed urls, and put them into the queue '''
            filtered_urls = self.filter_url(extracted_urls)
            for new_url in filtered_urls:
                self.url_queue.put((new_url, depth + 1))

        self.__dump_cached_urls()


class URLCrawler(Crawler):
    def save_content(self, url, depth, html_pyquery):
        parse_list = urlsplit(url)
        host = parse_list[0] + '://' + parse_list[1]
        with open(self._out_dir + 'savedLinks.txt', 'a') as outfile:
            outfile.write(host + '\n')


class ImageCrawler(Crawler):
    def save_content(self, url, depth, html_pyquery):
        all_imgs = html_pyquery('img').map(lambda i, element: PyQuery(element)('img').attr('src'))
        for raw_url in all_imgs:
            image_name = raw_url.split('/')[-1]
            words = image_name.split('.')
            suffix = ''
            if len(words) > 1:
                suffix = words[-1]
            print(image_name + ', ' + suffix)
            try:
                img_url = quote(raw_url, safe='!#$&()*+,-./:;=?@_~\'', encoding='utf-8')
                req = Request(img_url)
                response = urlopen(req)
                content = response.read()

                m = hashlib.md5()
                m.update(content)
                content_hash = m.hexdigest()
                filename = content_hash + '.' + suffix
                if os.path.exists(self._out_dir + filename):
                    continue
                with open(self._out_dir + filename, 'wb') as image_file:
                    image_file.write(content)
            except URLError as e:
                logging.warning('Request: URLError: %s\n\tRaw URL: %s', e.reason, raw_url)
                continue
            except Exception as e:
                logging.warning('Request: %s : %s\n\tRaw URL: %s', type(e), e, raw_url)
                continue


class ICML2019Crawler(Crawler):
    """
    Parameters: -a https://icml.cc/Conferences/2019/Schedule?type=Poster -d 0
    """
    @staticmethod
    def heading_author(_, element):
        entry = PyQuery(element)
        heading = entry('.maincardBody').text()
        author_list = entry('.maincardFooter').text().split(' · ')
        return heading, author_list

    def save_content(self, url, depth, html_pyquery):
        all_entries = html_pyquery('.maincard')
        heading_authors = all_entries.map(ICML2019Crawler.heading_author)
        with open(self._out_dir + 'ICML2019.csv', 'w', encoding='utf8') as outfile:
            for heading, author_list in heading_authors:
                outfile.write('\t'.join([heading] + author_list) + '\n')


class CVPR2019Crawler(Crawler):
    """
    Parameters: -a http://cvpr2019.thecvf.com/program/main_conference -d 0
    """
    def save_content(self, url, depth, html_pyquery):
        topic_title_author_dic = {}
        all_tables = html_pyquery('table')
        for a_table in all_tables.items():
            entries = a_table('tr').filter(lambda i, this: PyQuery(this).attr('class') != 'blue-bottom')
            current_topic = ''
            current_id = 0
            current_title = ''
            current_authors = []
            for idx, field in enumerate(entries('td')):
                if idx % 6 == 0:
                    if field.text is not None:
                        current_topic = field.text
                elif idx % 6 == 3:
                    current_title = field.text
                elif idx % 6 == 4:
                    current_authors = field.text.split(';')
                elif idx % 6 == 5:
                    current_id = field.text
                    if current_id not in topic_title_author_dic.keys():
                        topic_title_author_dic[current_id] = [current_topic, current_title] + current_authors

        with open(self._out_dir + 'CVPR2019.csv', 'w', encoding='utf8') as outfile:
            for id, topic_title_author_list in topic_title_author_dic.items():
                outfile.write('\t'.join([id] + topic_title_author_list) + '\n')


def main():
    # if sys.modules['idlelib']:
    #     sys.argv.extend(input("Args: ").split())

    # args.init_urls = 'http://www.baidu.com'
    # args.depth = 3

    parser = argparse.ArgumentParser(description='A crawler for website')
    parser.add_argument('-a', type=str, required=True, metavar='WebAddr', dest='init_urls',
                        help='Specify the Website Address')
    parser.add_argument('-d', type=int, default=1, metavar='CrawlDepth', dest='depth', help='Specify the Crawler Depth')
    parser.add_argument('-o', type=str, default='./', metavar='OutputDir', dest='out_dir',
                        help='Specify the Output Directory')
    args = parser.parse_args()

    crawler = CVPR2019Crawler(args)
    crawler.run()


if __name__ == '__main__':
    main()

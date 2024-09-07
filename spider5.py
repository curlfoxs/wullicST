# coding: utf-8

import re
import queue
import threading
from contextlib import contextmanager
from functools import reduce

from bs4 import BeautifulSoup
import psycopg2
import asyncio
import aiohttp

# from log import now

# logging.debug

# 这个编程实践对我意义非凡，amazing！
# 1. 直观概念
# 无论是正则表达式匹配的理解、线程concur（threading、threadpoolexecutor、future）、
# async（promise）和sync、
# py func object（deco、map、filter、reduce、genne、yield）上下文管理器context、
# #系统和子系统、类和子类、data和procedure、数据库database、速度匹配buffer缓冲区和queue和task任务
# 让我对python的语言特性（__call__, metaclass， 语法和动作的映射关系），和一些cs普shi.的概念有了更大的兴趣

# 2. 分析方法
# 从cs、network、通信等角度分析关键路径，和性能可优化的方向
# 通过比较各关键步骤的执行时间分析目前软体的缺陷在哪里，和系统理论知识比对
# 并发/并行的关键都是速度是否匹配、让不同的逻辑流在不同的组件/部件下运行，达到总体吞吐量和响应时间的最优化
# 系统和子系统的认识，通过对事物的直观概念和理解，重新确立data和procedure的本质，建立软体系统框架（系统组件和类，工作流程和线程，关键路径和性能优化地方）
# 关键技术的直观点在哪：例如并发（线程、信号量、信号）、异步（同步）、语言特性（deco、context、metaclass、runtime-object）等等
# 正则表达式的练习和掌握（？的问题，匹配的问题，search、match、findall、fullmatch的问题，分组匹配子串的问题，向前向后看包含与不包含的问题等等）


# 3. fuck your father 的requests库和 ssl 验证，看来python一些基础的库出问题的话会对语言本身造成很大的
# gevent、threadpoolexecutor 和 request、urllib3等库使用时，在处理ssl的时候，会产生
# max stack堆栈溢出的错误

logDuringSwitch = False
thread_nums = 16  # （8，100） is nice

threadDBLock = threading.Lock()


def threadDBLocker(func):
    def tWrap(*args, **kwargs):
        threadDBLock.acquire()
        rv = func(*args, **kwargs)
        threadDBLock.release()
        return rv
    return tWrap


class PageDB:
    def __init__(self, dbname, config={}):
        self.dbname = dbname
        self.key = 'url'
        self.table = 'subjectTestt2'
        self.unvisited_table = 'unvisited'
        self.text = 'text'

    def dbconn(func):
        @threadDBLocker
        def wrap(self, *args, **kwargs):
            with psycopg2.connect("""
            dbname={}
            user=postgres
            password=3832
            """.format(self.dbname)) as conn:
                self.cur = conn.cursor()
                self._init_table()
                rv = func(self, *args, **kwargs)
                return rv
        return wrap

    def _init_table(self):
        # Data items table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS {self.table} (
            id serial NOT NULL PRIMARY KEY,
            {self.key} text,
            {self.text} text,
            mark smallint)
        """.format(self=self))
        # Unvisited pages
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS {self.unvisited_table} (
            id serial NOT NULL PRIMARY KEY,
            {self.key} text)
        """.format(self=self))

    @dbconn
    def fetch_oneitem(self, key):
        self.cur.execute("""
        SELECT *
        FROM {self.table}
        WHERE {self.key} = (%s)
        """.format(self=self), (key,))
        return self.cur.fetchone()

    @dbconn
    def fetch_allkeys(self):
        self.cur.execute("""
        SELECT {self.key}
        FROM {self.table}
        """.format(self=self))
        return [row[0] for row in self.cur.fetchall()]

    @dbconn
    def put_dataitems(self, items):
        lt = [(item['url'], item['text'], 0) for item in items]
        self.cur.executemany("""
        INSERT INTO  {self.table} ({self.key}, {self.text}, mark)
        VALUES (%s, %s, %s)
        """.format(self=self), lt)

    @dbconn
    def fetch_unvisited_pages(self, num):
        self.cur.execute("""
        SELECT *
        FROM {self.unvisited_table}
        ORDER by id
         """.format(self=self))  # desc 是后十行
        rows = self.cur.fetchall()
        ids = [(row[0],) for row in rows]
        pages = [row[1] for row in rows]
        # self.cur.execute('DROP TABLE {}'.format(self.unvisited_table))
        self.cur.executemany("""
        DELETE
        FROM {self.unvisited_table}
        WHERE id = (%s)
        """.format(self=self), ids)
        return pages

    @dbconn
    def put_unvisited_pages(self, pages):
        lp = [(page, ) for page in pages]
        self.cur.executemany("""INSERT INTO  {self.unvisited_table} ({self.key})
                            VALUES (%s)""".format(self=self), lp)

    @dbconn
    def delete_dataitems(self, items):
        lt = [(item,) for item in items]
        self.cur.executemany("""
        DELETE
        FROM {self.table}
        WHERE {self.key} = (%s)
        """.format(self=self), lt)


class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.bufferlock = threading.Lock()

    def BufLocker(func):
        def wrap(self, *w, **kw):
            self.bufferlock.acquire()
            rv = func(self, *w, **kw)
            self.bufferlock.release()
            return rv
        return wrap


class SpiSavor(Worker):
    def __init__(self, boss, configs={}):
        super().__init__()
        self.boos = boss
        self.db = PageDB('test')
        # self.db = PageDB('bangumi')
        self.buffer = queue.Queue()
        self.blacklist = self._init_blacklist()
        self.fullthre = 500
        self.fullsem = threading.Condition()

    def _init_blacklist(self):
        urls = self.db.fetch_allkeys()
        return set(urls)

    def visited_filter(self, url):
        if url in self.blacklist:
            return False
        else:
            return True
        # row = self.db.fetch_oneitem(url)
        # return True if row == None else False

    def run(self):
        while True:
            with self.fullsem:
                while self.buffer.qsize() < self.fullthre:
                    self.fullsem.wait()
                self.writeDB_items()

    def receive_item(self, item):
        self.buffer.put(item)
        self.blacklist.add(item['url'])

        with self.fullsem:
            if (self.buffer.qsize() >= self.fullthre):
                self.fullsem.notify()

    def writeDB_items(self):
        num = self.buffer.qsize()
        print('[{}] savor.writeDB_items: buffer_size={}\n'.format(now(), num))
        items = [self.buffer.get() for _ in range(num)]
        if len(items) > 0:
            self.db.put_dataitems(items)

    def send_unvisited_pages(self, num):
        return self.db.fetch_unvisited_pages(num)

    def writeDB_unvisited_pages(self, pages):
        return self.db.put_unvisited_pages(pages)

    def delete_items(self, items):
        self.db.delete_dataitems(items)
        for item in items:
            if item in self.blacklist:
                self.blacklist.remove(item)


class SpiParser(Worker):
    def __init__(self, boss, hosts, configs={}):
        super().__init__()
        self.boss = boss
        self.buffer = queue.Queue()
        self.hosts = hosts
        self.filters = [self.filter1]
        self.filters.append(self.filter2)  # something like this

    def run(self):
        while True:
            self.parser()
        # while(True):
        #     threads = [threading.Thread(target=self.parser)for _ in range(5)]
        #     for t in threads:
        #         t.start()
        #     for t in threads:
        #         t.join()

    def parser(self):
        url, text = self.getResp()
        if self.filter1(url):
            item, pages = self.parse(url, text)
            self.sendItem(item)
            # filter_func = reduce(lambda x, y: x.__and__(y), self.filters)
            # pages = filter(filter_func, pages)
            for f in self.filters:
                pages = filter(f, pages)
            for page in pages:
                self.sendPage(page)
            # print("""[{}] parser.run:  buf_size={},
            # finished page: {}.\n""".format(now(), self.buffer.qsize(), url))

    @Worker.BufLocker
    def getResp(self):
        return self.buffer.get()

    @Worker.BufLocker
    def sendItem(self, item):
        self.boss.savor.receive_item(item)

    @Worker.BufLocker
    def sendPage(self, page):
        self.boss.searcher.receive_page(page)

    def receiveResp(self, resp):
        self.buffer.put(resp)

    def filter1(self, url):
        return self.boss.savor.visited_filter(url)

    def filter2(self, url):
        # 匹配 book 或者 subsite
        rex = r'.*(book|subject|blog|person).*'
        return False if re.search(rex, url) is None else True

    def parse(self, url, text):
        item = {'url': url, 'text': text}  # dict 类型保存网页数据, 格式由config给出
        pages = []  # pages to visit
        soup = BeautifulSoup(text, 'html.parser')
        reduce(self.selector, soup.select('a[href]'), pages)
        reduce(self.selector, soup.select('link[href]'), pages)
        # for page in pages:
        #     print('url:{}\n'.format(len(list(pages))))
        return item, pages

    def selector(self, result, tag):
        # 1. 包含bgm.tv或bangumi.tv的urls
        # 2. 排除以结尾js、css、jpg、png、ico、image的url；排除以javascript开头的url
        # 3. url统一为'https://bangumi.tv/'开头
        rex2 = r'((?<!javascript).(?!\.js|\.css|\.jpg|\.ico|\.png|/tag/|\?|#))*'
        rex3 = r'^((http[s]?:)?(//)?/?)'  # 匹配http协议开头
        url = tag.get('href')
        if re.fullmatch(rex2, url):
            url = re.sub(r'bgm.tv', 'bangumi.tv', url)
            # url = re.sub(r'bangumi.tv', 'www.bangumi.tv', url)
            if url.startswith('http') or url.find('bangumi.tv') != -1:
                url = re.sub(rex3, 'https://', url)
                if url.find('bangumi.tv') != -1:
                    result.append(url)
            else:
                # all we thout to this type: "(https://bangumi.tv)/suject/1029"
                url = re.sub(rex3, 'https://www.bangumi.tv/', url)
                result.append(url.rstrip('/'))
        return result


bufferLock = threading.Lock()


class SpiSearcher(Worker):
    def __init__(self, boss, src, configs={}):
        super().__init__()
        self.boss = boss
        self.src = src
        self.buffer_para1 = 100
        self.buffer_para2 = 3000
        self.buffer = queue.LifoQueue()
        self.prioQueue = queue.PriorityQueue()
        self.duplicated = set()
        self._init_buffer()

    def run(self):
        self.search()
        pass

    def _init_buffer(self):
        # self.boss.savor.delete_items(self.src)
        for u in self.src:
            self.receive_page(u)
        pages = self.boss.savor.send_unvisited_pages(self.buffer_para1)
        for p in pages:
            self.receive_page(p)
        print("init buffer size = {}".format(self.buffer.qsize()))

    def search(self):
        while True:
            self.sendurl()
            bufferLock.acquire()
            print("flag of have_storeonce = {}, buff's size={}".format /
                  (self.have_storedonce, self.buffer.qsize()))

    def sendurl(self):
        for _ in range(self.buffer_para2):
            url = self.buffer.get()
            self.boss.downloader.receive_url(url)
        print("searcher  buff's size={}".format(self.buffer.qsize()))

    def receive_page(self, url):
        if url not in self.duplicated:
            self.duplicated.add(url)
            self.buffer.put(url)

    # store buffer once, for next spider
    def store_buffer(self):
        size = self.buffer.qsize()
        pages = [self.buffer.get() for _ in range(size)]
        print("""hey guys, for next spider, we have duty to
 store {} unvisited pages""".format(size))
        self.boss.savor.writeDB_unvisited_pages(pages)


class SpiDownloader(Worker):
    def __init__(self, boss, configs={}):
        super().__init__()
        self.boss = boss
        self.buffer = queue.Queue()
        self.concur = 150
        self.failresp = 0
        self.timeoutresp = 0
        self.success = 0

    def run(self):
        """
        Start downloader.

        It will continuelly pick url from its bufferdownload page,
        and send responses to parser's buffer
        """
        while True:
            urls = []
            size = self.buffer.qsize()
            if size < 300 and bufferLock.locked():
                bufferLock.release()
            elif not bufferLock.locked():
                bufferLock.acquire()
            num = self.concur if self.concur < size else size
            for i in range(num):
                urls.append(self.buffer.get())
            if len(urls) == 0:
                continue
            self.failresp = 0
            self.timeoutresp = 0
            self.success = 0
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            loop = asyncio.get_event_loop()
            tasks = asyncio.gather(*[self.download_onepage(u) for u in urls])
            loop.run_until_complete(tasks)
            size = self.buffer.qsize()
            print("""[{0}] downloader: buf_size={1}, success {self.success} pages
                     resp_failed {self.failresp} pages,
                     timeout_failed {self.timeoutresp} pages\n
                  """.format(now(), size, self=self))

    # Amazing ~~~~~~``
    async def download_onepage(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=6) as resp:
                    if resp is not None and resp.status == 200:
                        text = await resp.text()
                        self.success += 1
                        self.sendResp((url, text))
                    else:
                        self.failresp += 1
        except Exception:
            # print('[{}] {}'.format(now(), e))
            self.timeoutresp += 1
            self.receive_url(url)

    def receive_url(self, url):
        self.buffer.put(url)

    @Worker.BufLocker
    def sendResp(self, resp):
        self.boss.parser.receiveResp(resp)


class Spider:
    """
    1. seacher : Gives next pages base on priority, not duplicated
unvisited (eg. dfs, bfs, way to search)
    2. downlaoder : Receive a url, send request and download response
    3. parser : Receive a response of http method, produce items
to save and pages to visit
    4. savor : Save item to database , and maintain a blacklist(visited)
    """
    def __init__(self, src=[], hosts=[], configs={}):
        self.savor = SpiSavor(self)
        self.parser = SpiParser(self, hosts)
        self.downloader = SpiDownloader(self)
        self.searcher = SpiSearcher(self, src)

    @contextmanager
    def ProtectCtx(self):
        print('Hei, welcome to my amazing crawl world.!')
        try:
            yield
        except Exception as e:
            raise e
        finally:
            self.end()

    def start(self):
        with self.ProtectCtx():
            self.savor.start()
            self.parser.start()
            self.downloader.start()
            self.searcher.start()
            # self.searcher.join()
            # self.downloader.join()
            # self.parser.join()
            self.savor.join()

    def end(self):
        print("hey, guys, for beautiful future, keep open and wait please....")
        self.searcher.store_buffer()
        self.savor.writeDB_items()
        print("hey, guys, all job's done, you can close it now. Thanks~~~~~~")


if __name__ == '__main__':
    src = ['https://bangumi.tv/subject/1', 'https://bangumi.tv/subject/9',
           'https://bangumi.tv/subject/2', 'https://bangumi.tv/subject/5']
    spi = Spider(src)
    spi.start()

# 1. wirte configs - mainly about db info and item info,
# also includes supported hosts and priority urls type
configs = {
    'dbname': 'bangumi',
    'table': 'book',
    'hosts': ['bangumi.tv', 'bgm.tv'],
    'priority': ['book', 'suject'],
    'item': {
        'key': 'text',
        'text': 'text',
        'marked': 'smallint',
        'author': 'text',
        'img': 'bytes'
    }
}

# 2. overwirte some "pareser" function, like parse(),
# to customlize your crawl behavior

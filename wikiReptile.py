from bs4 import BeautifulSoup
import urllib.request as ulb
import re


class WikiReptile(object):

    def __init__(self, base_key, deep, relation_path, context_path):
        self.__urlsList = set()
        self.__baseUrl = 'https://en.wikipedia.org'
        self.__baseKey = base_key
        self.__deep = deep
        self.__contextPath = context_path
        self.__relationPath = relation_path

    def __add_url(self, url):
        self.__urlsList.add(url)

    def get_urls_len(self):
        return len(self.__urlsList)

    # 局部广度优先遍历
    def save_list(self, key_url, start_urls, deep_count=0):
        deep_count += 1
        if self.__deep < deep_count:
            return
        print('初始网页 %s 包含链接数 %s' % (key_url[6:], str(len(start_urls))))
        count = 0
        listMap = {}
        for url in start_urls:
            count += 1
            string = key_url[6:] + "\t->\t" + url[6:]
            print('\t%s 保存关系 %s' % (str(count), string))
            self.__apend_relation(self.__relationPath, string)
            if url not in self.__urlsList:
                print('\t\t保存网页 %s' % url[6:])
                success = self.__apend_html("https://en.wikipedia.org%s" % url, self.__contextPath)
                if not success:
                    continue
                self.__urlsList.add(url)
                url_List = self.__get_urls("https://en.wikipedia.org%s" % url)
                if isinstance(url_List, list) and url_List != []:
                    listMap[url] = url_List
        for key, value in listMap.items():
            self.save_list(key, value, deep_count)

    def __open_url(self, url):
        try:
            the_link = ulb.urlopen(url, timeout=10)
            the_read = the_link.read()
        except BaseException:
            print('当前连接失败...放弃并继续')
            return None
        else:
            return the_read

    def __apend_relation(self, path, string):
        try:
            list_file = open(path, "a+", encoding='utf-8')
        except BaseException:
            print('%s打开失败...放弃并继续' % path)
        else:
            try:
                list_file.write(string + "\n")
            except BaseException:
                print('关系写入失败...放弃并继续')
            finally:
                list_file.close()

    def __apend_html(self, the_url, the_path):
        the_read = self.__open_url(the_url)
        if the_read is None:
            return False
        the_html = BeautifulSoup(str(the_read, encoding="utf-8"), "lxml")
        title = self.__get_title(the_html)
        try:
            file = open(the_path, "a+", encoding='utf-8')
        except BaseException:
            print('%s打开失败...放弃并继续' % the_path)
            return False
        else:
            try:
                file.write('1 ' + title + "\n")
                content = self.__get_content(the_html)
                for ele in content:
                    file.write(ele + "\n")
                    if '2 References' in ele:
                        references = self.__get_references(the_html)
                        if references is not None:
                            for reference in references:
                                file.write(reference + "\n")
                file.write("\n" + "=" * 20 + "\n\n")
            except BaseException:
                print('正文写入失败...放弃并继续')
                return False
            finally:
                file.close()
        return True

    def __get_title(self, the_html):
        title = the_html.find("h1", {"id": "firstHeading"}).get_text()
        return title.replace('/', '_')

    def __get_content(self, the_html):
        content = the_html.find("div", {"id": "bodyContent"})
        contents = []
        for ele in content.findAll({"h1", "h2", "h3", "h4", "h5", "h6", "p"}):
            # file.write(str(ele)[2] + " " + ele.get_text() + "\n")
            contents.append(str(ele)[2] + " " + ele.get_text())
        return contents

    def __get_references(self, the_html):
        try:
            content = the_html.find("ol", {"class": "references"})
            refers = content.findAll("li")
        except AttributeError:
            return None
        # print(content.get_text())
        referecces = []
        count = 0
        for ele in refers:
            count += 1
            referecces.append("[" + str(count) + "] " + ele.get_text())
            # print(str(count) + "\t" + ele.get_text())
        return referecces

    def __get_urls(self, init_url):
        the_read = self.__open_url(init_url)
        if the_read is None:
            return
        html = BeautifulSoup(str(the_read, encoding="utf-8"), "lxml")
        content = html.find("div", {"id": "bodyContent"})
        urls = []
        for link in content.findAll("a", href=re.compile("^(/wiki/)((?!:).)*$")):
            if 'href' in link.attrs:
                if link.attrs['href'] not in self.__urlsList:
                    urls.append(link.attrs['href'])
        return urls

    def run(self):
        self.__add_url(self.__baseKey)
        self.__apend_html(self.__baseUrl + self.__baseKey, self.__contextPath)
        urlList = self.__get_urls(self.__baseUrl + self.__baseKey)
        if isinstance(urlList, list) and urlList != []:
            self.save_list(self.__baseKey, urlList)


# 爬取英文维基百科https://en.wikipedia.org网页内容
baseKey = '/wiki/Computer'
webDeep = 1
saveUrl = "C:/Users/dzy/PycharmProjects"
relationFileName = "/url_link_list.txt"
contextFileName = "/wiki.txt"
##
# 传入参数
#   base_key         初始网页（不包含维基基础地址）
#   webDeep          爬取深度
#   deep             爬取深度（一个网页到下一个网页为一个深度）
#   relation_path    关系保存文件地址
#   context_path     正文保存文件地址
wiki_reptile = WikiReptile(baseKey, webDeep, saveUrl + relationFileName, saveUrl + contextFileName)
wiki_reptile.run()
print("\t所有网页数： " + str(wiki_reptile.get_urls_len()))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import requests
import sys
import re
import math
import random
import time

from mysql_helper import MySql


class CNVDCrawler(object):
    """

    Attributes:
        session:
        base_url
    """

    def __init__(self):
        self.session = requests.session()
        self.base_url = 'http://www.cnvd.org.cn/'
        self.requests_headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'en-US',
                                'Accept-Encoding': 'gzip, deflate',
                                'Connection': 'keep-alive',
                                'Cache-Control': 'max-age=0'
                                }
        self.cves = []

    def try_conn(self, url, times):
        for time in xrange(times):
            try:
                return requests.get(url, timeout=10, allow_redirects=True, headers=self.requests_headers)
            except requests.RequestException:
                pass
        print 'try connect url fail: %s' % url
        raise requests.RequestException

    def try_post(self, url, data, times):
        for time in xrange(times):
            try:
                return self.session.post('http://www.cnvd.org.cn/flaw/typeResult', timeout=5,
                                         data=data, headers=self.requests_headers)
            except requests.RequestException:
                pass

        print 'try post url fail: %s' % url
        sys.exit(-1)

    def get_cnvd_id(self, last_cnvd=''):
        url = 'http://www.cnvd.org.cn/flaw/typelist?typeId=31'
        # self.try_conn(url, 3)
        resp = self.try_post('http://www.cnvd.org.cn/flaw/typeResult', {'typeId': '31'}, 3)
        pages_url_re = r'Next</a><span>.+?(\d+).+?</span>'
        pages_url_pattern = re.compile(pages_url_re)
        total = int(pages_url_pattern.search(resp.content).group(1))

        # max_offset_re = r'max=(\d+?).+?offset=(\d+?)'
        # max_offset_pattern = re.compile(max_offset_re)
        # max_offset = max_offset_pattern.findall(pages_url[-2])
        # the second from last element indicates the CNVD title number
        print 'total CNVD title %d detected on website' % total
        for offset_base in xrange(int(math.ceil(total / 100.0))):
            cve_title_url = self.base_url + 'flaw/typeResult?typeId=31&max=100&offset=' + str(offset_base * 100)
            print 'get url: %s' % cve_title_url
            try:
                resp = self.try_conn(cve_title_url, 2)
            except requests.RequestException:
                print 'try get cve title id page error'
                continue
            # print resp.content
            cve_title_re = r'href="/flaw/show/(CNVD.+?)"'
            cve_title_pattern = re.compile(cve_title_re)
            cves_per_page = cve_title_pattern.findall(resp.content)
            print 'detected %d CNVD title in this page' % len(cves_per_page)
            for cve in cves_per_page:
                if cve == last_cnvd:
                    print '%d piece of new CNVD information detected.' % len(self.cves)
                    return
                self.cves.append(cve)

            time.sleep(random.randint(1, 3))

        print '%d piece of new CNVD information detected.' % len(self.cves)

    def insert_cnvd_title(self):
        host = '127.0.0.1'
        username = 'root'
        password = 'tanxiao123'
        port = 3306
        database = 'vulnerability_info'

        mysql = MySql(host, username, password, database, port)
        tbname = 'cnvd_net_device'

        for x in self.cves:
            cnvd = {'cnvd': x}
            mysql.insert(tbname, cnvd)

        mysql.commit()

    def cnvd_info(self, cnvd_id):
        url = self.base_url + 'flaw/show/' + cnvd_id
        try:
            resp = self.try_conn(url, 2)
        except requests.RequestException:
            print '%s get information page fail' % cnvd_id
            return

        content = resp.text.encode('utf8')
        # threat_rank_re = repr('危害级别')[1:-1] + r'.+?</span>(.+?)\('
        # threat_rank_pattern = re.compile(threat_rank_re, re.S)
        # threat_rank_match = threat_rank_pattern.search(content)
        # if threat_rank_match:
        #     print threat_rank_match.group(1).strip()
        #
        # effect_device_re = repr('影响产品')[1:-1] + r'.+?<td>(.+?)</td>'
        # effect_device_pattern = re.compile(effect_device_re, re.S)
        # effect_device_match = effect_device_pattern.search(content)
        # if effect_device_match:
        #     print effect_device_match.group(1)
        info_res = [repr('危害级别')[1:-1] + r'.+?</span>(.+?)\(',
                    repr('影响产品')[1:-1] + r'.+?<td>(.+?)</td>',
                    r'CVE ID</td>.+?>(CVE.+?) </a>',
                    repr('漏洞描述')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('参考链接')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('漏洞解决方案')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('厂商补丁')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('验证信息')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('报送时间')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('收录时间')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('更新时间')[1:-1] + r'.+?<td>(.+?)</td>',
                    repr('漏洞附件')[1:-1] + r'.+?<td>(.+?)</td>']

        info_patterns = map(lambda x: re.compile(x, re.S), info_res)
        info_matchs = map(lambda x: x.search(content), info_patterns)
        info_list = map(lambda x: x.group(1).strip().decode('utf8') if x else '', info_matchs)

        # replace \t in effect devices segment
        info_list[1] = info_list[1].replace('\t', '').replace('<br/>', '').replace('\r\n\r\n', '|| ')
        # replace \t \n in description segment
        info_list[3] = info_list[3].replace('\t', '').replace('<br/>\n', '||').replace('\n', '').replace('<br/>', '')

        # replace \t <br/> tag in solution segment
        info_list[5] = info_list[5].replace('\t', '').replace('<br/>\n', '||').replace('<br/>', '')
        for x in info_list:
            print x
            print '---------------'



if __name__ == '__main__':
    cnvd_crawler = CNVDCrawler()
    # cnvd_crawler.get_cnvd_id('CNVD-2015-06206')

    # print cnvd_crawler.cves[random.randint(0, len(cnvd_crawler.cves))]

    cnvd_crawler.cnvd_info('CNVD-2015-03975')

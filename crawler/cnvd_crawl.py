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

    def __init__(self, sql_helper):
        self.sql_help = sql_helper
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
        for x in xrange(times):
            try:
                return requests.get(url, timeout=10, allow_redirects=True, headers=self.requests_headers)
            except requests.RequestException:
                pass
        print 'try connect url fail: %s' % url
        raise requests.RequestException

    def try_post(self, url, data, times):
        for x in xrange(times):
            try:
                return requests.post('http://www.cnvd.org.cn/flaw/typeResult', timeout=5,
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
        tbname = 'cnvd_net_device'

        for x in self.cves:
            cnvd = {'cnvd': x}
            self.sql_help.insert(tbname, cnvd)

        self.sql_help.commit()

    def cnvd_info(self, cnvd_id):
        url = self.base_url + 'flaw/show/' + cnvd_id
        try:
            resp = self.try_conn(url, 2)
        except requests.RequestException:
            print '%s get information page fail' % cnvd_id
            return

        content = resp.text.encode('utf-8')
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
        info_res = [repr('危害级别')[1:-1] + r'.+?</span>(.+?)[\(<]',      # 0
                    repr('影响产品')[1:-1] + r'.+?<td>(.+?)</td>',      # 1
                    r'CVE ID</td>.+?>(CVE.+?) </a>',                    # 2
                    repr('漏洞描述')[1:-1] + r'.+?<td>(.+?)</td>',      # 3
                    repr('参考链接')[1:-1] + r'.+?<td>(.+?)</td>',      # 4
                    repr('漏洞解决方案')[1:-1] + r'.+?<td>(.+?)</td>',  # 5
                    repr('厂商补丁')[1:-1] + r'.+?<td>(.+?)</td>',      # 6
                    repr('验证信息')[1:-1] + r'.+?<td>(.+?)</td>',      # 7
                    repr('报送时间')[1:-1] + r'.+?<td>(.+?)</td>',      # 8
                    repr('收录时间')[1:-1] + r'.+?<td>(.+?)</td>',      # 9
                    repr('更新时间')[1:-1] + r'.+?<td>(.+?)</td>',      # 10
                    repr('漏洞附件')[1:-1] + r'.+?<td>(.+?)</td>']      # 11

        info_patterns = map(lambda x: re.compile(x, re.S), info_res)
        info_matchs = map(lambda x: x.search(content), info_patterns)
        info_list = map(lambda x: x.group(1).strip().decode('utf-8') if x else '', info_matchs)
        info_list = map(lambda  x: x.replace("'", '"'), info_list)

        info_list[1] = info_list[1].strip().replace('\t', '').replace('<br/>\r\n\r\n', '||')[:-5]
        info_list[1] = '暂无' if info_list[1] == '' else info_list[1]
        info_list[3] = info_list[3].strip().replace('\t', '').replace('<br/>\r\n\r\n', '\n')[:-5]
        info_list[4] = '||'.join(re.compile(r'"(http.+?)"').findall(info_list[4]))
        info_list[5] = info_list[5].strip().replace('\t', '').replace('<br/>\r\n\r\n', '\n')[:-5]
        if 'patchInfo' in info_list[6]:
            info_list[6] = '||'.join(map(lambda x: x[0] + ':' + x[1],
                                     re.compile(r'=("/patchInfo.+?")>(.+?)</a>').findall(info_list[6])))
        else:
            pass

        print '-' * 20
        print '--' + cnvd_id + '---'
        for x in info_list:
            print x.encode('gbk', errors='replace').decode('gbk')

        return info_list

    def cnvd_update(self, cnvd, cnvd_title, if_commit):
        tbname = 'cnvd_net_device'
        condition = '`cnvd` = "' + cnvd_title + '"'
        cnvd_info = {
            'threat_rank': cnvd[0],
            'effect_device': cnvd[1],
            'cve': cnvd[2],
            'description': cnvd[3],
            'reference_url': cnvd[4],
            'upload_time': time.mktime(time.strptime(cnvd[8], '%Y-%m-%d')),
            'publish_time': time.mktime(time.strptime(cnvd[9], '%Y-%m-%d')),
            'modify_time': time.mktime(time.strptime(cnvd[10], '%Y-%m-%d')),
            'poc': cnvd[7],
            'solution': cnvd[5],
            'patch': cnvd[6],
            'attachment': cnvd[11]
        }

        self.sql_help.update(tbname, cnvd_info, condition)
        if if_commit:
            self.sql_help.commit()

    def cnvds_update_database(self):
        query_sql = 'SELECT cnvd FROM cnvd_net_device WHERE threat_rank IS NULL LIMIT 500'
        self.sql_help.query(query_sql)
        empty_cnvds = self.sql_help.fetch_all()
        print empty_cnvds
        for empty_cnvd in empty_cnvds:
            empty_cnvd = empty_cnvd['cnvd']
            cnvd_info = cnvd_crawler.cnvd_info(empty_cnvd)
            try:
                cnvd_crawler.cnvd_update(cnvd_info, empty_cnvd, True)
            except requests.RequestException, e:
                time.sleep(random.randint(8, 12))
                continue
            else:
                print 'update database successfully'
                time.sleep(random.randint(1, 2))

if __name__ == '__main__':
    host = '127.0.0.1'
    username = 'root'
    password = 'tanxiao123'
    port = 3306
    database = 'vulnerability_info'

    mysql = MySql(host, username, password, database, port)
    cnvd_crawler = CNVDCrawler(mysql)
    cnvd_crawler.cnvds_update_database()
    # cnvd_crawler.get_cnvd_id('CNVD-2015-06206')

    # print cnvd_crawler.cves[random.randint(0, len(cnvd_crawler.cves))]

    # info_list = cnvd_crawler.cnvd_info('CNVD-2015-03975')
    # cnvd_crawler.cnvd_update(info_list, 'CNVD-2015-03975', True)

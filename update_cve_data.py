#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import urllib2
import xml.sax
import decode_xml
import time
from mysql_helper import MySql


def download_cve_file(url, file_name):
    """download cve xml file from given url

    Args:
        url: xml file url, for downloading
        file_name: xml store file name
    """

    url = url
    file_name = file_name
    u = urllib2.urlopen(url)
    f = open('resource/' + file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    # download big file(large than 3Mb, using block

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status += chr(8) * (len(status) + 1)    # use '\r' to keep the print in the same line
        print status,

    f.close()

if __name__ == '__main__':
    host = '127.0.0.1'
    username = 'root'
    password = 'tanxiao123'
    port = 3306
    database = 'vulnerability_info'

    mysql = MySql(host, username, password, database, port)
    tbname = 'cve'

    mysql.query('SELECT cve FROM vulnerability_info.cve ORDER BY cve DESC LIMIT 1')
    last_cve_name = mysql.fetch_row()[0]
    print 'last CVE name: %s' % last_cve_name

    url = 'https://cve.mitre.org/data/downloads/allitems-cvrf-year-2015.xml'
    file_name = url.split('/')[-1]
    # download_cve_file(url, file_name)

    parser = xml.sax.make_parser()

    # Todo find the latest cve number in the database
    handler = decode_xml.CVEHandler(last_cve_name)
    parser.setContentHandler(handler)

    parser.parse('resource/' + file_name)

    new_cves = handler.cves

    print 'detected %d new CVE titles' % len(new_cves)
    for new_cve in new_cves:
        # [self.title, self.noteDescription, self.published, self.modified, self.cve, self.references])
        urls = ''
        descriptions = ''
        for reference in new_cve[5]:
            urls += reference[0] + '|||'
            descriptions += reference[1] + '|||'

        cve_info = {'cve': new_cve[0],
                    'note': new_cve[1],
                    'publish_time': time.mktime(time.strptime(new_cve[2], '%Y-%m-%d')) if new_cve[2] != '' else -1,
                    'modify_time': time.mktime(time.strptime(new_cve[3], '%Y-%m-%d')) if new_cve[3] != '' else -1,
                    'urls': urls,
                    'descriptions': descriptions,
                    }
        mysql.insert(tbname, cve_info)

    mysql.commit()





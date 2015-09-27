#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import urllib2
import xml.sax
import decode_xml


def download_cve_file(url, file_name):
    url = url
    file_name = file_name
    u = urllib2.urlopen(url)
    f = open('resource/' + file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status += chr(8) * (len(status) + 1)
        print status,

    f.close()

if __name__ == '__main__':
    url = 'https://cve.mitre.org/data/downloads/allitems-cvrf-year-2015.xml'
    file_name = url.split('/')[-1]
    download_cve_file(url, file_name)

    parser = xml.sax.make_parser()

    # Todo find the latest cve number in the database
    latest_cve = ''
    handler = decode_xml.CVEHandler(lastest_cve)
    parser.setContentHandler(handler)

    parser.parse('resource/' + file_name)

    new_cves = handler.cves
    for new_cve in new_cves:
        # Todo update sql
        pass



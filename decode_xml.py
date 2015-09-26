#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import xml.sax


class CVEHandler(xml.sax.ContentHandler):
    """sax handler class

    sax event handler class, for the consideration of CVE xml size,
    we don't use ElementsTree(need to much memories)

    Attributes:

    """

    def __init__(self):
        self.currentData = ''
        self.title = ''
        self.notes = []
        self.cve = ''
        self.references = []
        self.url = ''
        self.description = ''

        self.cves = []

    def startElement(self, name, attrs):
        if name == 'Vulnerability':
            self.title = ''
            self.notes = []
            self.cve = ''
            self.references = []
            self.url = ''
            self.description = ''
            print 'start'

        self.currentData = name

    def characters(self, content):
        if self.currentData == 'Title':
            print content
            self.title = content
        elif self.currentData == 'Note':
            self.notes.append(content)
        elif self.currentData == 'CVE':
            print content
            self.cve = content

    def endElement(self, name):
        if name == 'Vulnerability':
            print 'end'
            self.cves.append([self.title, self.notes, self.cve])


if __name__ == '__main__':
    parser = xml.sax.make_parser()

    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    Handler = CVEHandler()
    parser.setContentHandler(Handler)

    parser.parse('resource/allitems-cvrf-year-2015.xml')

    print len(Handler.cves)
    print Handler.cves[0]
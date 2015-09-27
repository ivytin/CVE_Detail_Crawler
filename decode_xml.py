#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import xml.sax
import random


class CVEHandler(xml.sax.ContentHandler):
    """sax handler class

    sax event handler class, for the consideration of CVE xml size,
    we don't use ElementsTree(need to much memories)

    Attributes:

    """

    def __init__(self):
        self.currentData = ''
        self.title = ''
        self.noteDescription = ''
        self.published = ''
        self.modified = ''
        self.cve = ''
        self.url = ''
        self.description = ''
        self.references = []

        self.referenceCount = -1
        self.cveCount = -1

        self.cves = []

    def startElement(self, name, attrs):
        if name == 'Vulnerability':
            self.title = ''
            self.noteDescription = ''
            self.published = ''
            self.modified = ''
            self.cve = ''
            self.url = ''
            self.description = ''
            self.references = []

            self.cveCount += 1
            self.referenceCount = -1
            self.currentData = name

        elif name == 'Note' and self.cveCount >= 0:
            if attrs['Type'] == 'Description':
                self.currentData = 'NoteDescription'
            elif attrs['Type'] == 'Other':
                if attrs['Title'] == 'Published':
                    self.currentData = 'Published'
                elif attrs['Title'] == 'Modified':
                    self.currentData = 'Modified'

        elif name == 'Reference' and self.cveCount >= 0:
            self.referenceCount += 1
            self.references.append(['', ''])
            self.currentData = name
        else:
            self.currentData = name

    def characters(self, content):
        if self.cveCount >= 0:
            if self.currentData == 'Title':
                self.title = content
            elif self.currentData == 'NoteDescription':
                self.noteDescription += content
            elif self.currentData == 'Published':
                self.published = content
            elif self.currentData == 'Modified':
                self.modified = content
            elif self.currentData == 'CVE':
                self.cve = content
            elif self.currentData == 'URL':
                self.references[self.referenceCount][0] = content
            elif self.currentData == 'Description':
                self.references[self.referenceCount][1] = content

    def endElement(self, name):
        if name == 'Vulnerability' and self.cveCount >= 0:
            self.cves.append([self.title, self.noteDescription.replace('\n', ' '), self.published,
                              self.modified, self.cve, self.references])

        self.currentData = ''


if __name__ == '__main__':
    parser = xml.sax.make_parser()

    Handler = CVEHandler()
    parser.setContentHandler(Handler)

    parser.parse('resource/allitems-cvrf.xml')
    # parser.parse('resource/test.xml')

    print len(Handler.cves)
    print Handler.cves[random.randint(0, 1000)]


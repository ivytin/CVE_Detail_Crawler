#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import xml.sax


class CVEHandler(xml.sax.ContentHandler):
    """sax handler class

    sax event handler class, for the consideration of CVE xml size,
    we don't use ElementsTree(need to much memories)

    Attributes:
        currentData: current xml node when parser traverse
        title: cve title
        nodeDescription: cve description in Note node
        published: cve publish time in Note node
        modified: cve modified time in Note node
        cve: cve number
        url: cve reference url
        description: cve reference description
        references: cve reference list
        referenceCount: count the reference number in every cve node
        cveCount: count the cve number
        skip： skip all cve number less than this value
    """

    def __init__(self, skip=''):
        """init Handler and inner vars

        Args:
            skip: assignment the self.skip

        Returns:

        """

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

        self.skip = skip

    def startElement(self, name, attrs):
        """call back when reach every element tag start

        Args:
            <Note Type="1"></Note>
            name: element name/tags, Note here
            attrs: element attributes dict, {'Type': '1'}

        Return:

        """

        if name == 'Vulnerability':
            # reach the vulnerability element's beginning
            # initialize all vars for recording a vulnerability

            self.title = ''
            self.noteDescription = ''
            self.published = ''
            self.modified = ''
            self.cve = ''
            self.url = ''
            self.description = ''
            self.references = []

            # cveCount ++
            self.cveCount += 1
            self.referenceCount = -1
            self.currentData = name

        # the Notes element is a little bit complex
        # node name is decided by the attribute in the attrs var

        elif name == 'Note' and self.cveCount >= 0:
            if attrs['Type'] == 'Description':
                self.currentData = 'NoteDescription'
            elif attrs['Type'] == 'Other':
                if attrs['Title'] == 'Published':
                    self.currentData = 'Published'
                elif attrs['Title'] == 'Modified':
                    self.currentData = 'Modified'

        # find a reference node

        elif name == 'Reference' and self.cveCount >= 0:
            self.referenceCount += 1
            self.references.append(['', ''])    # add a pair to record the url and description in each reference
            self.currentData = name
        else:
            self.currentData = name

    def characters(self, content):
        """tag content process function

        record the node content and distinguish the node name by currentData
        which given by startElement()

        Args:
            <Note Type="1">content</Note>
            content: here refer to the content

        Return:

        """

        if self.cveCount >= 0:
            if self.currentData == 'Title':
                self.title += content
                self.title = self.title.replace('\n', '')
            elif self.currentData == 'NoteDescription':
                self.noteDescription += content
                self.noteDescription = self.noteDescription.replace('\n', ' ')
            elif self.currentData == 'Published':
                self.published += content
                self.published = self.published.replace('\n', '')
            elif self.currentData == 'Modified':
                self.modified += content
                self.modified = self.modified.replace('\n', '')
            elif self.currentData == 'CVE':
                self.cve += content
                self.cve = self.cve.replace('\n', '')
            elif self.currentData == 'URL':
                self.references[self.referenceCount][0] = content
            elif self.currentData == 'Description':
                self.references[self.referenceCount][1] = content

    def endElement(self, name):
        """when tag end call back this function

        Args:
            name: tag name

        """
        if name == 'Vulnerability' and self.cveCount >= 0 and (self.title > self.skip):
            self.cves.append([self.title, self.noteDescription, self.published,
                              self.modified, self.cve, self.references])        # add a cve node to the list
        self.currentData = ''         # reset the element name


if __name__ == '__main__':
    parser = xml.sax.make_parser()

    Handler = CVEHandler()
    parser.setContentHandler(Handler)

    parser.parse('resource/allitems-cvrf-year-2015.xml')
    # parser.parse('resource/cvrf-template.xml')
    # parser.parse('resource/allitems-cvrf.xml')

    print len(Handler.cves)
    # print Handler.cves
    # print Handler.cves[random.randint(0, 1000)]
#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Version 0.1.3 2017-06-27 (C) Anselmo Blanco Dominguez (Oxigenai)
#
# Tested in only one environment, with this característics:
# - Ubuntu 16.04
# - Python 3.5.2
# - MBOX files from Thunderbird 45.8.0
# - Thunderbird, files and script in the same machine
# - before and after running "Condense Folder" routine from Thunderbird
#
# Usage: mb2e.py path/to/mbox
#
# Funcionality
# The script:
# - Create a directorie with the name of the MBOX file appended with '.__eml__'
# - For each mail encountred in the file the script get the Message-ID
# - Each mail is saved in the created directorie with the name "Message-ID".eml
#
# To do:
# - clean and enhance the code quality
# - test in other environments
# - better logger
# - treat the second extraction of emails, such as archiving deleted emails and
#     not rewriting equal emails.
# - detect bad e-mails and bad attachments
# - save separated header and body
#
# Future related projects:
# - Extract attachments to subdirectory
# - Extract all parts
#
# Obs.: The complexity of the script stems from the fact that it creates a
# small check if the default EMLs tab within MBOX is valid. As far as I can
# tell, Thuderbird himself takes care of this, but I think it's best not to
# assume that everything is ok.
#
# Version 0.1.3 2017-06-27
# History
# . Clean Mozilla tags
# . remove old code
#
# Version 0.1.2 2017-06-27
# . Rewrite using class
# . Bug in detecting message id
# . Logger
# . Evolving
# . Mantein old code for comparison
#
# Version 0.1.1 2017-06-26
# . Much mo more tests (same plataform)
# . Sane "eml" file name
# . Evolving header regex
#
# Version 0.1 2017-04-11 (C) Anselmo Blanco Dominguez (Oxigenai)
# . First version

import os
import sys

import re


debug = 2
cleanMozilla = True


def p(l, str, *arg, **argv):
    global debug
    if debug >= l:
        print(' '*l, str, *arg, **argv)


class Mbox():
    NONE = 0
    READ = 1
    HEADERCANDIDATE = 2
    COPY = 3
    END = 4

    state = NONE
    nLine = 0
    nLineLimit = 0
    header = []
    msgId = ''
    line = ''
    mailDir = ''
    mbox = None
    eml = None

    def __init__(self, mboxName):
        p(3, '>__init__')
        try:
            self.mbox = open(mboxName, 'r', encoding="latin-1")
        except Exception as e:
            p(0, 'Can not open mbox file to read "{}"'.format(mboxName))
        p(2, 'mbox file = {}'.format(mboxName))
        p(2, 'mbox file opened')
        self.mailDir = '{}.__mb2e__'.format(mboxName)
        p(2, 'mailDir = {}'.format(self.mailDir))
        self.setState(self.READ)

    def __del__(self):
        p(3, '>__del__')
        self.mbox.close()

    def initEml(self):
        p(3, '>initEml')
        if not self.eml:
            if not os.path.isdir(self.mailDir):
                os.mkdir(self.mailDir)

            if self.msgId:
                name = self.msgId
            else:
                name = 'line_{}'.format(self.nLine)
            mailName = '{}.eml'.format(name)
            transCharacters = {'/': '_pathbar_'}
            mailFileName = "".join(transCharacters[c]
                                   if c in transCharacters
                                   else c
                                   for c in mailName
                                   ).rstrip()
            mailFileName = os.path.join(self.mailDir, mailFileName)
            p(2, 'eml file = {}'.format(mailFileName))
            try:
                self.eml = open(mailFileName, 'w')
            except Exception as e:
                p(0, 'Can not open mail file to write "{}"'.format(mboxName))

    def endEml(self):
        p(3, '>endEml')
        self.eml.close()
        self.eml = None

    def cleanLine(self):
        return self.line.strip('\n')

    def extract(self):
        p(3, '>extract')
        for self.line in self.mbox:
            self.nLine += 1
            if self.nLineLimit > 0 and self.nLine > self.nLineLimit:
                self.setState(self.END)
                break
            line = self.cleanLine()
            p(4, 'extract nLine = {}; line = "{}"{}'.format(
                self.nLine, line[:30],
                '...' if line[30:] else ''))
            self.processLine()

    def headerLine(self):
        line = self.cleanLine()
        if cleanMozilla and (
                re.search('^X-Mozilla-Status2?: .*$', line) or
                re.search('^X-Mozilla-Keys: .*$', line)):
            return
        self.header.append(self.line)

    def processLine(self):

        def isIniHeader():
            line = self.cleanLine()
            result = bool(
                re.search('^From $', line)
                or re.search('^From - ... ... .. ..:..:.. ....$', line)
                )
            p(3, 'isIniHeader line = "{}" = {}'.format(
                line[:20], result))
            return result

        def isInsideHeader():
            line = self.cleanLine()
            result = bool(
                re.search('^[^ ]+: .*$', line)
                or re.search('^\s+[^ ].*$', line)
                )
            p(3, 'isInsideHeader line = "{}" = {}'.format(
                line[:20], result))
            return result

        def ifGetMessageId():
            line = self.cleanLine()
            p(3, 'ifGetMessageId')
            reMsgId = re.search('^Message-I[dD]: <(.*)>', line)
            if reMsgId is not None:
                self.msgId = reMsgId.group(1)
                p(3, 'ifGetMessageId line = "{}"; self.msgId = "{}"'
                    .format(line[:20], self.msgId))

        def isEndHeader():
            line = self.cleanLine()
            result = bool(re.search('^ *$', line))
            p(3, 'isEndHeader line = "{}" = {}'.format(
                line[:20], result))
            return result

        p(3, '>processLine')
        if self.state in (self.READ, self.COPY):
            p(4, 'processLine state == READ or COPY')
            if isIniHeader():
                p(4, 'processLine isIniHeader')
                self.setState(self.HEADERCANDIDATE)
                # self.headerLine()

        elif self.state == self.HEADERCANDIDATE:
            p(4, 'processLine state == HEADERCANDIDATE')
            if isInsideHeader():
                p(4, 'processLine isInsideHeader')
                ifGetMessageId()
                self.headerLine()
            else:
                p(4, 'processLine not isInsideHeader')
                if isEndHeader() and len(self.header) > 1:
                    p(4, 'processLine isEndHeader and has header')
                    self.setState(self.COPY)
                else:
                    p(4, 'processLine not isEndHeader or hasn''t header')
                    self.setState(self.READ)

        if self.state == self.COPY:
            p(4, 'processLine state == COPY')
            self.eml.write(self.line)

    def setState(self, state):
        if self.state == state:
            return
        self.state = state
        p(3, '>setState = {}'.format(self.state))

        if self.state == self.READ:
            p(4, 'setState = READ')
            self.header = []

        if self.state == self.HEADERCANDIDATE:
            p(4, 'setState = HEADERCANDIDATE')
            self.msgId = None

        if self.state in (self.COPY, self.END):
            p(4, 'setState = COPY or END')
            if self.eml is not None:
                p(4, 'setState - andEml')
                self.endEml()
                p(4, 'self.eml = {}'.format(self.eml))

        if self.state == self.COPY:
            p(4, 'setState = COPY')
            p(4, 'setState - initEml')
            self.initEml()
            p(4, 'setState - for self.header')
            for headerLine in self.header:
                self.eml.write(headerLine)
            p(4, 'setState - empty self.header')
            self.header = []


if __name__ == '__main__':
    mboxName = sys.argv[1]

    mbox = Mbox(mboxName)
    # mbox.nLineLimit = 0
    # p(1, 'mbox.nLineLimit = {}'.format(mbox.nLineLimit))

    mbox.extract()

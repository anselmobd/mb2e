#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import sys
import re

import gettext

from oxy.arg import parse as argparse
from oxy.verbose import VerboseOutput


class Mbox():
    NONE = 0
    READ = 1
    HEADERCANDIDATE = 2
    COPY = 3
    END = 4

    vOut = None
    state = NONE
    nLine = 0
    header = []
    msgId = ''
    line = ''
    mailDir = ''
    mbox = None
    eml = None

    def __init__(self):
        self.parseArgs()
        self.vOut = VerboseOutput(self.args.verbosity)
        self.vOut.prnt('->... __init__', 4)

        self.openMbox()
        self.extract()

    def __del__(self):
        if self.vOut is not None:
            self.vOut.prnt('->__del__', 4)
        if self.mbox is not None:
            self.mbox.close()

    def openMbox(self):
        self.vOut.prnt('->openMbox', 4)
        try:
            self.mbox = open(self.args.mboxFile, 'r', encoding="latin-1")
        except Exception as e:
            self.vOut.prnt('Can not open mbox file to read "{}"'.format(
                self.args.mboxFile), 0)
            sys.exit(21)
        self.vOut.prnt('mbox file = {}'.format(self.args.mboxFile), 1)
        self.vOut.prnt('mbox file opened', 1)
        self.mailDir = '{}.__mb2e__'.format(self.args.mboxFile)
        self.vOut.prnt('mailDir = {}'.format(self.mailDir), 1)
        self.setState(self.READ)

    def initEml(self):
        self.vOut.prnt('->initEml', 4)
        if not self.eml:
            if not os.path.isdir(self.mailDir):
                os.mkdir(self.mailDir)

            if self.msgId:
                name = self.msgId
            else:
                name = 'line_{}'.format(self.nLine)
            mailName = '{}.eml'.format(name)
            transCharacters = {'/': '_pathbar_',
                               '$': '_dolar_',
                               '-': '_'}
            mailFileName = "".join(transCharacters[c]
                                   if c in transCharacters
                                   else c
                                   for c in mailName
                                   ).rstrip()
            mailFileName = os.path.join(self.mailDir, mailFileName)
            self.vOut.prnt('eml file = {}'.format(mailFileName), 2)
            try:
                self.eml = open(mailFileName, 'w')
            except Exception as e:
                self.vOut.prnt('Can not open mail file to write "{}"'.format(
                    mailFileName), 0)

    def endEml(self):
        self.vOut.prnt('->endEml', 4)
        self.eml.close()
        self.eml = None

    def cleanLine(self):
        return self.line.strip('\n')

    def extract(self):
        self.vOut.prnt('->extract', 4)
        for self.line in self.mbox:
            self.nLine += 1
            if self.args.lineLimit > 0 and self.nLine > self.args.lineLimit:
                self.setState(self.END)
                break
            line = self.cleanLine()
            self.vOut.prnt('extract nLine = {}; line = "{}"{}'.format(
                self.nLine, line[:30],
                '...' if line[30:] else ''), 4)
            self.processLine()

    def headerLine(self):
        line = self.cleanLine()
        if self.args.cleanMozilla and (
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
            self.vOut.prnt('isIniHeader line = "{}" = {}'.format(
                line[:20], result), 3)
            return result

        def isInsideHeader():
            line = self.cleanLine()
            result = bool(
                re.search('^[^ ]+: .*$', line)
                or re.search('^\s+[^ ].*$', line)
                )
            self.vOut.prnt('isInsideHeader line = "{}" = {}'.format(
                line[:20], result), 3)
            return result

        def ifGetMessageId():
            line = self.cleanLine()
            self.vOut.prnt('ifGetMessageId', 3)
            reMsgId = re.search('^Message-I[dD]: <(.*)>', line)
            if reMsgId is not None:
                self.msgId = reMsgId.group(1)
                self.vOut.prnt(
                    'ifGetMessageId line = "{}"; self.msgId = "{}"'
                    .format(line[:20], self.msgId), 3)

        def isEndHeader():
            line = self.cleanLine()
            result = bool(re.search('^ *$', line))
            self.vOut.prnt('isEndHeader line = "{}" = {}'.format(
                line[:20], result), 3)
            return result

        self.vOut.prnt('->processLine', 4)
        if self.state in (self.READ, self.COPY):
            self.vOut.prnt('processLine state == READ or COPY', 4)
            if isIniHeader():
                self.vOut.prnt('processLine isIniHeader', 4)
                self.setState(self.HEADERCANDIDATE)
                # self.headerLine()

        elif self.state == self.HEADERCANDIDATE:
            self.vOut.prnt('processLine state == HEADERCANDIDATE', 4)
            if isInsideHeader():
                self.vOut.prnt('processLine isInsideHeader', 4)
                ifGetMessageId()
                self.headerLine()
            else:
                self.vOut.prnt('processLine not isInsideHeader', 4)
                if isEndHeader() and len(self.header) > 1:
                    self.vOut.prnt('processLine isEndHeader and has header', 4)
                    self.setState(self.COPY)
                else:
                    self.vOut.prnt(
                        'processLine not isEndHeader or hasn''t header', 4)
                    self.setState(self.READ)

        if self.state == self.COPY:
            self.vOut.prnt('processLine state == COPY', 4)
            self.eml.write(self.line)

    def setState(self, state):
        if self.state == state:
            return
        self.state = state
        self.vOut.prnt('>setState = {}'.format(self.state), 3)

        if self.state == self.READ:
            self.vOut.prnt('setState = READ', 4)
            self.header = []

        if self.state == self.HEADERCANDIDATE:
            self.vOut.prnt('setState = HEADERCANDIDATE', 4)
            self.msgId = None

        if self.state in (self.COPY, self.END):
            self.vOut.prnt('setState = COPY or END', 4)
            if self.eml is not None:
                self.vOut.prnt('setState - andEml', 4)
                self.endEml()
                self.vOut.prnt('self.eml = {}'.format(self.eml), 4)

        if self.state == self.COPY:
            self.vOut.prnt('setState = COPY', 4)
            self.vOut.prnt('setState - initEml', 4)
            self.initEml()
            self.vOut.prnt('setState - for self.header', 4)
            for headerLine in self.header:
                self.eml.write(headerLine)
            self.vOut.prnt('setState - empty self.header', 4)
            self.header = []

    def parseArgs(self):
        parser = argparse.ArgumentParser(
            description=_('Extract EML files from MBox to subdirectory\n'
                          'version 0.1.6 2017-06-28'),
            epilog="(c) Anselmo Blanco Dominguez (Tussor & Oxigenai)",
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument(
            "mboxFile",
            help='name of the MBox file')
        parser.add_argument(
            "-c", "--cleanMozilla",
            action="store_true",
            help='clean Mozilla tags in EML')
        parser.add_argument(
            "-l", "--lineLimit",
            type=int,
            default=0,
            help='number of lines of mboxFile to be processed (if > 0)')
        parser.add_argument(
            "-v", "--verbosity", action="count", default=0,
            help="increase output verbosity")
        self.args = parser.parse_args()


if __name__ == '__main__':
    mb2eGT = gettext.translation('mb2e', 'po', fallback=True)
    mb2eGT.install()

    mbox = Mbox()

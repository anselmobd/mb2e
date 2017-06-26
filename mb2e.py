#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Version 0.1 2017-04-11 (C) Anselmo Blanco Dominguez (Oxigenai)
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
# - logger
# - Treat the second extraction of emails, such as archiving deleted emails and
#     not rewriting equal emails.
#
# Future related projects:
# - Extract attachments to subdirectory
# - Extract all parts
#
# Obs.: The complexity of the script stems from the fact that it creates a
# small check if the default EMLs tab within MBOX is valid. As far as I can
# tell, Thuderbird himself takes care of this, but I think it's best not to
# assume that everything is ok.

import os
import sys

import re


def p(l, str, *arg, **argv):
    global debug
    if debug >= l:
        print(' ', str, *arg, **argv)


debug = 2
lineLimit = -1000000

mboxName = sys.argv[1]

p(1, 'mbox {}'.format(mboxName))

mailDir = '{}.__eml__'.format(sys.argv[1])

eml = None
msgId = ''
bNewMail = False
bCandidate = False
cabLines = 0
lCandidate = []
i = 0
iLin = 0
try:
    with open(mboxName, 'r', encoding="latin-1") as mbox:
        for line in mbox:
            iLin += 1
            test = line.strip('\n')
            p(9, 'iLin = {}'.format(iLin))
            p(9, 'test = {}'.format(test))

            if lineLimit > 0 and iLin > lineLimit:
                sys.exit(99)

            if bCandidate:
                p(8, test[:20], end=' | ')
                if re.search('^[^ ]+: .*$', test) \
                   or re.search('^\s+[^ ].*$', test):
                    cabLines += 1
                    p(9, 'cabLines = {}'.format(cabLines))
                    lCandidate.append(line)
                    reMsgId = re.search('^Message-ID: <(.*)>', test)
                    if reMsgId is not None:
                        msgId = reMsgId.group(1)
                        p(8, 'msgId {}'.format(msgId))

                else:
                    p(8, '')
                    p(8, test[:20])
                    p(8, '{} cab lines'.format(cabLines))
                    if re.search('^ *$', test) and cabLines > 0:
                        p(8, 'cab valido')
                        bNewMail = True
                    else:
                        p(8, 'cab invalido')
                    bCandidate = False
                    cabLines = 0

            else:
                p(9, 'not bCandidate')
                if re.search('^From $', test) \
                   or re.search('^From - ... ... .. ..:..:.. ....$', test):
                    p(8, 'Candidate!!!', iLin, test)
                    bCandidate = True
                    lCandidate.append(line)

            if not bCandidate:
                if bNewMail:
                    bNewMail = False
                    if eml is not None:
                        eml.close()
                    i += 1

                    if not os.path.isdir(mailDir):
                        os.mkdir(mailDir)

                    # mailName = 'mail{:06}-{}.eml'.format(i,    msgId)
                    mailName = '{}.eml'.format(msgId)
                    transCharacters = {'/': '_pathbar_'}
                    mailFileName = "".join(transCharacters[c]
                                           if c in transCharacters
                                           else c
                                           for c in mailName).rstrip()
                    p(2, mailFileName)
                    mailFileName = os.path.join(mailDir, mailFileName)
                    eml = open(mailFileName, 'w')

                if len(lCandidate) > 0:
                    del lCandidate[0]
                    for candLine in lCandidate:
                        eml.write(candLine)
                    lCandidate = []
                if eml is not None:
                    eml.write(line)
finally:
    if eml is not None:
        eml.close()

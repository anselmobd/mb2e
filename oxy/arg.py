#!/usr/bin/python3
# -*- coding: utf8 -*-

import gettext

gettext.bindtextdomain('argparse', 'po')
gettext.textdomain('argparse')

if __name__ != '__main__':
    import argparse
    parse = argparse

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2015,16 - Walter Bender <walter@sugarlabs.org>
# This is for the .po file.
# How to use: script.py file-old.po file-new.po

# This script will mine an old po file for any untranslated strings in a new po file.

import os
import re
import sys
import codecs


def mine_from_po_to_po(oldfilename, newfilename, ignore_case):
    oldfd = codecs.open(oldfilename, "r", "UTF-8")
    newfd = codecs.open(newfilename, "r", "UTF-8")
    output = codecs.open('tmp.po', "w", "UTF-8")

    olddict = {}
    for line in oldfd:
        if line[0:5] == 'msgid':
            key = line[7:-2]
        if line[0:6] == 'msgstr':
            value = line[8:-2]
            if value == '':
                continue;
            if ignore_case:
                olddict[key.lower()] = value;
            else:
                olddict[key] = value;

    newdict = {}
    for line in newfd:
        msgstr_flag = False
        if line[0:5] == 'msgid':
            key = line[7:-2]
        if line[0:6] == 'msgstr':
            value = line[8:-2]
            msgstr_flag = True

        if ignore_case:
            if msgstr_flag and value == '' and  key.lower() in olddict:
                print('found a match for %s' % (key))
                output.write('msgstr "%s"\n' % (olddict[key.lower()]))
            else:
                output.write(line);
        else:
            if msgstr_flag and value == '' and  key in olddict:
                output.write('msgstr "%s"\n' % (olddict[key]))
                print('found a match for %s' % (key))
            else:
                output.write(line);

    output.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("po2po source target [ignorecase]")
    elif len(sys.argv) == 4:
        ini = mine_from_po_to_po(sys.argv[1], sys.argv[2], True)
        print("Finished")
    else:
        ini = mine_from_po_to_po(sys.argv[1], sys.argv[2], False)
        print("Finished")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2016 - Walter Bender <walter@sugarlabs.org>

# Convert _('') strings in a JS file from one langauge to another
# using a PO file.
# How to use: js2js.py js-path po-file
# Outputs to js-file_

import os
import re
import sys
import glob
import string
import codecs


def mine_js_file(js_pathname, po_filename):

    # Read data from the existing PO file
    po_fd = codecs.open(po_filename, "r", "UTF-8")
    po_dict = {}

    # Build a translation dictionary from the PO file
    for line in po_fd:
        if line[0:5] == 'msgid':
            key = line[7:-2]
        elif line[0:6] == 'msgstr':
            if line[8:-2] != '':
                po_dict[key] = line[8:-2]


    # Mine strings for l23n from js files.
    js_files = glob.glob(os.path.join(js_pathname, 'js', '*js'))
    print(js_files)

    for path in js_files:
        basename = os.path.basename(path)
        js_fd = codecs.open(path, "r", "UTF-8")

        output = codecs.open(path[0:-3] + '_.js', 'w', "UTF-8")

        for line in js_fd:
            tmp = line.split("_('")
            if len(tmp) > 1:
                trans_line = tmp[0];
                for i in range(len(tmp)):
                    if i == 0:
                        continue;
                    trans_line += "_('"
                    tmp2 = tmp[i].split("')")
                    for j in range(len(tmp2)):
                        if j == 0:
                            if tmp2[j] in po_dict:
                                trans_line += po_dict[tmp2[j]]
                            else:
                                trans_line += tmp2[j]
                        else:
                            trans_line += tmp2[j]
                        if j < len(tmp2) - 1:
                            trans_line += "')"
                line = trans_line

            tmp = line.split('_("')
            if len(tmp) > 1:
                trans_line = tmp[0];
                for i in range(len(tmp)):
                    if i == 0:
                        continue;
                    trans_line += '_("'
                    tmp2 = tmp[i].split('")')
                    for j in range(len(tmp2)):
                        if j == 0:
                            if tmp2[j] in po_dict:
                                trans_line += po_dict[tmp2[j]]
                            else:
                                trans_line += tmp2[j]
                        else:
                            trans_line += tmp2[j]
                        if j < len(tmp2) - 1:
                            trans_line += '")'
            else:                
                trans_line = line;
            output.write(trans_line)

        js_fd.close()
        output.close()

    json_files = glob.glob(os.path.join(js_pathname, 'plugins', '*json'))
    print(json_files)

    for path in json_files:
        basename = os.path.basename(path)
        js_fd = codecs.open(path, "r", "UTF-8")

        output = codecs.open(path[0:-5] + '_.json', 'w', "UTF-8")

        for line in js_fd:
            tmp = line.split("_('")
            if len(tmp) > 1:
                print(tmp)
                trans_line = tmp[0];
                for i in range(len(tmp)):
                    print(i)
                    if i == 0:
                        continue;
                    trans_line += "_('"
                    tmp2 = tmp[i].split("')")
                    for j in range(len(tmp2)):
                        if j == 0:
                            if tmp2[j] in po_dict:
                                trans_line += po_dict[tmp2[j]]
                                print(po_dict[tmp2[j]])
                            else:
                                trans_line += tmp2[j]
                                print(tmp2[j])
                        else:
                            trans_line += tmp2[j]
                        if j < len(tmp2) - 1:
                            trans_line += "')"
                line = trans_line

            tmp = line.split('_("')
            if len(tmp) > 1:
                print(tmp)
                trans_line = tmp[0];
                for i in range(len(tmp)):
                    print(i)
                    if i == 0:
                        continue;
                    trans_line += '_("'
                    tmp2 = tmp[i].split('")')
                    for j in range(len(tmp2)):
                        if j == 0:
                            if tmp2[j] in po_dict:
                                trans_line += po_dict[tmp2[j]]
                                print(po_dict[tmp2[j]])
                            else:
                                trans_line += tmp2[j]
                                print(tmp2[j])
                        else:
                            trans_line += tmp2[j]
                        if j < len(tmp2) - 1:
                            trans_line += '")'
            else:                
                trans_line = line;
            output.write(trans_line)

        js_fd.close()
        output.close()

    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('js2js.py js-path po-file')
    else:
        ini = mine_js_file(sys.argv[1], sys.argv[2])

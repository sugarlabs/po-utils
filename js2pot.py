#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2016 - Walter Bender <walter@sugarlabs.org>
# Create or update pot file based on js files.
# How to use: script.py js-path pot-file
# Outputs to pot-file_

import os
import re
import sys
import glob
import codecs

js_list = []

js_trans_dict = {}  # //.TRANS:

js_line_numbers = []
js_line_numbers_dict = {}

def mine_path(js_files, root_path):

    trans_note = []
    for path in js_files:
        basename = os.path.basename(path)
        js_fd = codecs.open(path, "r", "UTF-8")

        count = 1
        for line in js_fd:
            tmp = line.split('//.TRANS:')
            if len(tmp) > 1:
                if not tmp[1] in trans_note:
                    trans_note.append(tmp[1])

            tmp = line.split('_("')            
            if len(tmp) > 1:
                for i in range(len(tmp)):
                    if i == 0:
                        continue
                    phrase = tmp[i].split('")')[0];

                    line_number = '%s/%s:%d' % (root_path, basename, count)
                    if phrase in js_list:
                        if not line_number in js_line_numbers_dict[phrase]:
                            js_line_numbers_dict[phrase].append(line_number)
                    else:
                        js_list.append(phrase)
                        js_line_numbers_dict[phrase] = [line_number]

                    if len(trans_note) > 0:
                        if phrase in js_trans_dict:
                            for note in trans_note:
                                js_trans_dict[phrase].append(note)
                        else:
                            js_trans_dict[phrase] = trans_note
                        trans_note = []

            tmp = line.split("_('")            
            if len(tmp) > 1:
                for i in range(len(tmp)):
                    if i == 0:
                        continue
                    phrase = tmp[i].split("')")[0];

                    line_number = '%s/%s:%d' % (root_path, basename, count)
                    if phrase in js_list:
                        if not line_number in js_line_numbers_dict[phrase]:
                            js_line_numbers_dict[phrase].append(line_number)
                    else:
                        js_list.append(phrase)
                        js_line_numbers_dict[phrase] = [line_number]

                    if len(trans_note) > 0:
                        if phrase in js_trans_dict:
                            for note in trans_note:
                                js_trans_dict[phrase].append(note)
                        else:
                            js_trans_dict[phrase] = trans_note
                        trans_note = []

            count += 1


def mine_js_files(js_pathname, pot_filename):

    # Read data from the existing POT file
    pot_fd = codecs.open(pot_filename, "r", "UTF-8")
    pot_list = []

    trans_note = []
    pot_trans_dict = {}  # //.TRANS:

    pot_line_numbers = []
    pot_line_numbers_dict = {}

    pot_header = ''
    end_of_header = False;

    for line in pot_fd:
        if line[0:2] == '#:':
            pot_line_numbers.append(line)
            end_of_header = True
        elif line[0:2] == '#.':
            trans_note.append(line)
            end_of_header = True
        elif line[0:5] == 'msgid':
            key = line[7:-2]
            pot_list.append(key)

            if not key == '':
                end_of_header = True

            if len(trans_note) > 0:
                pot_trans_dict[key] = trans_note
                trans_note = []

            if len(pot_line_numbers) > 0:
                pot_line_numbers_dict[key] = pot_line_numbers
                pot_line_numbers = []

        if not end_of_header:
            pot_header += line
    
    js_files = glob.glob(os.path.join(js_pathname, 'js', '*js'))
    print(js_files)
    mine_path(js_files, "js")

    js_files = glob.glob(os.path.join(js_pathname, 'js/utils', '*js'))
    print(js_files)
    mine_path(js_files, "js/utils")

    js_files = glob.glob(os.path.join(js_pathname, 'js/blocks', '*js'))
    print(js_files)
    mine_path(js_files, "js/blocks")

    js_files = glob.glob(os.path.join(js_pathname, 'js/turtleactions', '*js'))
    print(js_files)
    mine_path(js_files, "js/turtleactions")

    js_files = glob.glob(os.path.join(js_pathname, 'js/widgets', '*js'))
    print(js_files)
    mine_path(js_files, "js/widgets")

    js_files = glob.glob(os.path.join(js_pathname, 'js/js-export', '*js'))
    print(js_files)
    mine_path(js_files, "js/js-export")

    js_files = glob.glob(os.path.join(js_pathname, 'planet/js', '*js'))
    print(js_files)
    mine_path(js_files, "planet/js")

    rtp_files = glob.glob(os.path.join(js_pathname, 'plugins', '*rtp'))
    print(rtp_files)
    mine_path(rtp_files, "plugins")

    output = codecs.open(pot_filename + '_', 'w', "UTF-8")
    output.write(pot_header)
    
    for i in range(len(js_list)):
        for j in range(len(js_line_numbers_dict[js_list[i]])):
            output.write('#: %s\n' % (js_line_numbers_dict[js_list[i]][j]))

        if js_list[i] in js_trans_dict:
            for j in range(len(js_trans_dict[js_list[i]])):
                output.write('#.TRANS:%s' % (js_trans_dict[js_list[i]][j]))

        new_phrase = js_list[i].replace('"', '\\"')
        if len(new_phrase) > 0:
            output.write('msgid "%s"\nmsgstr ""\n\n' % (new_phrase))
        else:
            output.write('\n')

    for i in range(len(pot_list)):
        if pot_list[i] in js_list:
            continue;

        if pot_list[i] in pot_line_numbers_dict:
            for j in range(len(pot_line_numbers_dict[pot_list[i]])):
                output.write('%s' % (pot_line_numbers_dict[pot_list[i]][j]))

        if pot_list[i] in pot_trans_dict:
            for j in range(len(pot_trans_dict[pot_list[i]])):
                output.write('%s' % (pot_trans_dict[pot_list[i]][j]))

        output.write('#~msgid "%s"\n#~msgstr ""\n\n' % (pot_list[i]))

    output.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage is: python js2pot project_path pot_path')
    else:
        ini = mine_js_files(sys.argv[1], sys.argv[2])

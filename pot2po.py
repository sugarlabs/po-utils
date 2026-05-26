#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2026 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301  USA

#<walter@sugarlabs.org> Makes sure po files have all the strings found
#in a pot file.

# How to use: script.py pot-file po-file (optional second po file to be used
# for #TRANS help, e.g., add Spanish to Aymara strings.

# Outputs to po-file.po_

import argparse
import os
import re
import sys


def convert_pot_to_po(pot_filename, po_filename, trans_filename):

    # Read data from the existing POT file
    pot_fd = open(pot_filename, "r", encoding="utf-8")
    pot_list = []

    trans_note = []
    pot_trans_dict = {}  # //.TRANS

    line_numbers = []
    pot_line_numbers_dict = {}

    for line in pot_fd:
        if line[0:2] == "#:":
            line_numbers.append(line)
        elif line[0:2] == "#.":
            trans_note.append(line)
        elif line[0:5] == "msgid":
            key = line[7:-2]
            pot_list.append(key)

            if len(trans_note) > 0:
                pot_trans_dict[key] = trans_note
                trans_note = []

            if len(line_numbers) > 0:
                pot_line_numbers_dict[key] = line_numbers
                line_numbers = []

    pot_fd.close()

    # Read data from the trans file
    if trans_filename == "":
        trans_dict = {}
    else:
        trans_fd = open(trans_filename, "r", encoding="utf-8")

        trans_dict = {}

        for line in trans_fd:
            if line[0:2] == "#:":
                continue
            elif line[0:2] == "#.":
                continue
            elif line[0:5] == "msgid":
                key = line[7:-2]
            elif line[0:6] == "msgstr":
                trans_dict[key] = line[8:-2]

        trans_fd.close()

    po_fd = open(po_filename, "r", encoding="utf-8")
    po_dict = {}
    po_header = "msgid \"\"\nmsgstr \"\"\n"

    trans_note = []
    po_trans_dict = {}  # //.TRANS

    line_numbers = []
    po_line_numbers_dict = {}

    end_of_header = False;

    for line in po_fd:
        if line[0:2] == "#:":
            line_numbers.append(line)
        elif line[0:2] == "#.":
            end_of_header = True
            trans_note = line
        elif line[0:5] == "msgid":
            key = line[7:-2]
            if key != "":
                end_of_header = True
        elif line[0:7] == "#~msgid":
            key = line[9:-2]
            if key != "":
                end_of_header = True
        elif line[0:6] == "msgstr":
            if key == "":
                continue

            value = line[8:-2]
            po_dict[key] = value

            if len(trans_note) > 0:
                po_trans_dict[key] = trans_note
                trans_note = []

            if len(line_numbers) > 0:
                po_line_numbers_dict[key] = line_numbers
                line_numbers = []
        elif line[0:8] == "#~msgstr":
            if key == "":
                continue

            value = line[10:-2]
            po_dict[key] = value

            if len(trans_note) > 0:
                po_trans_dict[key] = trans_note
                trans_note = []

            if len(line_numbers) > 0:
                po_line_numbers_dict[key] = line_numbers
                line_numbers = []

        if not (end_of_header or line[0:5] == "msgid"):
            po_header += line

    po_fd.close()

    output = open(po_filename + "_", "w", encoding="utf-8")
    output.write(po_header)

    for i in range(len(pot_list)):
        if pot_list[i] == "":
            continue

        if pot_list[i] in pot_line_numbers_dict:
            for j in range(len(pot_line_numbers_dict[pot_list[i]])):
                output.write("%s" % (pot_line_numbers_dict[pot_list[i]][j]))

        if pot_list[i] in pot_trans_dict:
            for j in range(len(pot_trans_dict[pot_list[i]])):
                output.write("%s" % (pot_trans_dict[pot_list[i]][j]))

        if pot_list[i] in trans_dict:
            output.write("#. TRANS: %s\n" % (trans_dict[pot_list[i]]))

        if pot_list[i] in po_dict:
            output.write("msgid \"%s\"\nmsgstr \"%s\"\n\n" % (pot_list[i], po_dict[pot_list[i]]))
        else:
            output.write("msgid \"%s\"\nmsgstr \"\"\n\n" % (pot_list[i]))

    for phrase in po_dict:
        if not phrase in pot_list:
            if phrase in po_line_numbers_dict:
                for j in range(len(po_line_numbers_dict[phrase])):
                    output.write("%s\n" % (po_line_numbers_dict[phrase][j]))

            if phrase in pot_trans_dict:
                for j in range(len(pot_trans_dict[phrase])):
                    output.write("%s" % (pot_trans_dict[phrase][j]))

            if phrase in trans_dict:
                output.write("#. TRANS: %s\n" % (trans_dict[phrase]))

            output.write("#~msgid \"%s\"\n#~msgstr \"%s\"\n\n" % (phrase, po_dict[phrase]))

    output.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update PO files from POT.")
    parser.add_argument("pot", type=str, help="path to pot file")
    parser.add_argument("po", type=str, help="path to po file")
    parser.add_argument("--trans", type=str, default="", help="po file to use for trans notes")
    args = parser.parse_args()

    convert_pot_to_po(args.pot, args.po, args.trans)

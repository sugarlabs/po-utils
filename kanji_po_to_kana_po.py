#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2026 Walter Bender

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

import argparse
import os
import polib
import pykakasi

def convert_kanji_to_kana(kanji_po_path, kana_po_path, output_po_path, target_kana="hiragana"):
    """
    Fills untranslated strings in a Kana PO file with converted Kanji text from a source PO file.
    
    :param kanji_po_path: Path to the source PO file containing Kanji translations.
    :param kana_po_path: Path to the target PO file containing Kana translations (with blanks).
    :param output_po_path: Path where the newly filled PO file will be saved.
    :param target_kana: 'hiragana' or 'katakana' for the output style.
    """
    # 1. Initialize pykakasi converter properly using the modern API
    kakasielement = pykakasi.kakasi()
    
    # 2. Load both PO files
    print(f"Loading {kanji_po_path}...")
    kanji_po = polib.pofile(kanji_po_path)
    
    print(f"Loading {kana_po_path}...")
    kana_po = polib.pofile(kana_po_path)
    
    # Create a quick-lookup dictionary from the Kanji PO file {msgid: msgstr}
    kanji_dict = {entry.msgid: entry.msgstr for entry in kanji_po}
    
    converted_count = 0
    missing_source_count = 0
    
    # 3. Iterate through the Kana PO file to find untranslated entries
    for entry in kana_po:
        # Check if the entry is untranslated (msgstr is empty)
        if not entry.msgstr:
            # Look up the corresponding Kanji translation from the source file
            kanji_translation = kanji_dict.get(entry.msgid)
            
            if kanji_translation:
                # Modern pykakasi uses kakasielement.convert() directly
                result = kakasielement.convert(kanji_translation)
                
                # Reconstruct the string using the desired Kana type
                converted_string = ""
                for item in result:
                    if target_kana.lower() == "katakana":
                        converted_string += item['kana']
                    else:  # Defaults to hiragana
                        converted_string += item['hira']
                
                # Fill in the untranslated msgstr in the Kana file
                entry.msgstr = converted_string
                converted_count += 1
            else:
                missing_source_count += 1

    # 4. Save the modified Kana PO file
    kana_po.save(output_po_path)
    print("\n--- Processing Complete ---")
    print(f"Successfully converted and filled: {converted_count} entries.")
    if missing_source_count > 0:
        print(f"Warning: {missing_source_count} source strings were missing entirely from the Kanji PO file.")
    print(f"Saved output to: {output_po_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indent JSON")
    parser.add_argument("kanji", type=str, default="", help="path to Kanji po file")
    parser.add_argument("kana", type=str, default="", help="path to Kana po file") 
    parser.add_argument("output", type=str, help="path to output Kana po")
    args = parser.parse_args()

    # Run the script (change target_kana to 'katakana' if preferred)
    if os.path.exists(args.kanji) and os.path.exists(args.kana):
        convert_kanji_to_kana(args.kanji, args.kana, args.output, target_kana="hiragana")
    else:
        print("Error: Please check your file paths.")


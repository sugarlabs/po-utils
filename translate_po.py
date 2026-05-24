#!/usr/bin/env python3
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

# translate_po.py
# Translates untranslated strings in a PO file using Google Translate.
# Adds a comment to each auto-translated string marking it as machine-translated.
#
# Usage: python translate_po.py input.po output.po target_language
#   target_language: BCP-47 language code, e.g. 'fr', 'es', 'de', 'ja', 'pt-BR'
#
# Requires: pip install google-cloud-translate
# Authentication: set GOOGLE_APPLICATION_CREDENTIALS env var to your service
#   account JSON key file, or run on Google Cloud with appropriate IAM roles.
#
# Alternatively, uses the free deep-translator library as a fallback:
#   pip install deep-translator
# (no API key needed, but rate-limited)

import sys
import os
import re
import codecs
import time
import argparse

AUTO_TRANSLATE_COMMENT = '#. AUTOTRANSLATED: Google Translate'

def parse_po_file(path):
    """
    Parse a PO file into a list of entry dicts, preserving all structure.
    Each entry is a dict with keys:
      - 'comments': list of comment lines (including blank lines between entries)
      - 'msgid': the msgid string (unquoted)
      - 'msgstr': the msgstr string (unquoted)
      - 'raw_msgid': the original msgid line(s) as written in the file
      - 'raw_msgstr': the original msgstr line(s) as written in the file
      - 'obsolete': bool, True if this is a #~ entry
    Also returns the header block as a raw string.
    """
    entries = []
    header = ''

    with codecs.open(path, 'r', 'UTF-8') as f:
        lines = f.readlines()

    i = 0
    header_done = False
    pending_comments = []

    while i < len(lines):
        line = lines[i]

        # Blank line: flush pending comments as a spacer
        if line.strip() == '':
            if pending_comments:
                pending_comments.append(line)
            else:
                pending_comments.append(line)
            i += 1
            continue

        # Comment or flag lines
        if line.startswith('#') and not line.startswith('#~'):
            pending_comments.append(line)
            i += 1
            continue

        # Obsolete entries (#~msgid / #~msgstr) — preserve as-is
        if line.startswith('#~'):
            entry = {
                'comments': pending_comments,
                'obsolete': True,
                'raw': [line],
                'msgid': None,
                'msgstr': None,
            }
            pending_comments = []
            i += 1
            # Collect the rest of this obsolete block
            while i < len(lines) and (lines[i].startswith('#~') or lines[i].strip() == ''):
                if lines[i].strip() == '':
                    break
                entry['raw'].append(lines[i])
                i += 1
            entries.append(entry)
            continue

        # msgid
        if line.startswith('msgid '):
            raw_msgid_lines = [line]
            msgid = _unquote(line[6:].strip())
            i += 1
            # Multi-line msgid
            while i < len(lines) and lines[i].startswith('"'):
                msgid += _unquote(lines[i].strip())
                raw_msgid_lines.append(lines[i])
                i += 1

            # The very first msgid "" is the PO header
            if msgid == '' and not header_done:
                # Collect msgstr for header
                raw_msgstr_lines = []
                if i < len(lines) and lines[i].startswith('msgstr'):
                    raw_msgstr_lines.append(lines[i])
                    i += 1
                    while i < len(lines) and lines[i].startswith('"'):
                        raw_msgstr_lines.append(lines[i])
                        i += 1
                header = ''.join(pending_comments) + ''.join(raw_msgid_lines) + ''.join(raw_msgstr_lines)
                pending_comments = []
                header_done = True
                continue

            # msgstr
            raw_msgstr_lines = []
            msgstr = ''
            if i < len(lines) and lines[i].startswith('msgstr'):
                raw_msgstr_lines.append(lines[i])
                msgstr = _unquote(lines[i][7:].strip())
                i += 1
                while i < len(lines) and lines[i].startswith('"'):
                    msgstr += _unquote(lines[i].strip())
                    raw_msgstr_lines.append(lines[i])
                    i += 1

            entry = {
                'comments': pending_comments,
                'obsolete': False,
                'msgid': msgid,
                'msgstr': msgstr,
                'raw_msgid': raw_msgid_lines,
                'raw_msgstr': raw_msgstr_lines,
            }
            pending_comments = []
            entries.append(entry)
            continue

        # Anything else (e.g. unexpected lines) — treat as comment
        pending_comments.append(line)
        i += 1

    return header, entries


def _unquote(s):
    """Remove surrounding quotes and unescape a PO string value."""
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    elif s.startswith("'") and s.endswith("'"):
        s = s[1:-1]
    return s.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')


def _quote(s):
    """Escape and quote a string for writing as a PO msgstr value."""
    s = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
    return '"%s"' % s


def write_po_file(path, header, entries):
    """Write entries back to a PO file."""
    with codecs.open(path, 'w', 'UTF-8') as f:
        f.write(header)
        if header and not header.endswith('\n'):
            f.write('\n')
        for entry in entries:
            # Write pending comments/blank lines
            for c in entry['comments']:
                f.write(c)

            if entry.get('obsolete'):
                for line in entry['raw']:
                    f.write(line)
                f.write('\n')
                continue

            for line in entry['raw_msgid']:
                f.write(line)
            for line in entry['raw_msgstr']:
                f.write(line)
            f.write('\n')


def translate_entries(entries, target_lang, translator_fn):
    """
    For each entry with an empty msgstr, translate the msgid and fill in msgstr.
    Adds an AUTO_TRANSLATE_COMMENT to the entry's comments.
    """
    translated = 0
    skipped = 0

    for entry in entries:
        if entry.get('obsolete'):
            continue
        if not entry.get('msgid'):
            continue
        if entry['msgstr']:  # already translated
            continue

        msgid = entry['msgid']
        try:
            result = translator_fn(msgid, target_lang)
            entry['msgstr'] = result
            # Update the raw_msgstr line
            entry['raw_msgstr'] = ['msgstr %s\n' % _quote(result)]
            # Add auto-translate comment if not already present
            if not any(AUTO_TRANSLATE_COMMENT in c for c in entry['comments']):
                # Insert before any blank lines at the end of comments
                insert_at = len(entry['comments'])
                while insert_at > 0 and entry['comments'][insert_at - 1].strip() == '':
                    insert_at -= 1
                entry['comments'].insert(insert_at, AUTO_TRANSLATE_COMMENT + '\n')
            translated += 1
        except Exception as e:
            print('  WARNING: could not translate %r: %s' % (msgid[:60], e), file=sys.stderr)
            skipped += 1

    return translated, skipped


# ---------------------------------------------------------------------------
# Translator backends
# ---------------------------------------------------------------------------

def make_google_cloud_translator(project_id=None):
    """
    Uses the official Google Cloud Translation API v2 (requires API key or
    service account credentials via GOOGLE_APPLICATION_CREDENTIALS).
    pip install google-cloud-translate
    """
    from google.cloud import translate_v2 as translate
    client = translate.Client()

    def translate_fn(text, target_lang):
        result = client.translate(text, target_language=target_lang)
        return result['translatedText']

    return translate_fn


def make_googletrans_translator():
    """
    Uses the deep-translator library (no API key needed, actively maintained).
    pip install deep-translator
    Rate-limited -- adds a small delay between requests.
    """
    from deep_translator import GoogleTranslator

    def translate_fn(text, target_lang):
        time.sleep(0.2)  # be polite to avoid rate limiting
        return GoogleTranslator(source='auto', target=target_lang).translate(text)

    return translate_fn


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Auto-translate untranslated strings in a PO file using Google Translate.'
    )
    parser.add_argument('input_po', help='Input PO file path')
    parser.add_argument('output_po', help='Output PO file path')
    parser.add_argument('target_lang', help='Target language code (e.g. fr, es, de, ja, pt-BR)')
    parser.add_argument(
        '--backend', choices=['cloud', 'free'], default='free',
        help='Translation backend: "cloud" (Google Cloud Translation API, requires credentials) '
             'or "free" (googletrans, unofficial, no key needed). Default: free'
    )
    parser.add_argument(
        '--project', default=None,
        help='Google Cloud project ID (only needed for --backend=cloud)'
    )
    args = parser.parse_args()

    print('Parsing %s...' % args.input_po)
    header, entries = parse_po_file(args.input_po)

    untranslated = sum(
        1 for e in entries
        if not e.get('obsolete') and e.get('msgid') and not e.get('msgstr')
    )
    total = sum(1 for e in entries if not e.get('obsolete') and e.get('msgid'))
    print('Found %d untranslated strings out of %d total.' % (untranslated, total))

    if untranslated == 0:
        print('Nothing to do.')
        return

    print('Loading translator backend: %s' % args.backend)
    if args.backend == 'cloud':
        translator_fn = make_google_cloud_translator(args.project)
    else:
        translator_fn = make_googletrans_translator()

    print('Translating to %s...' % args.target_lang)
    translated, skipped = translate_entries(entries, args.target_lang, translator_fn)

    print('Writing %s...' % args.output_po)
    write_po_file(args.output_po, header, entries)

    print('Done. Translated: %d, Skipped (errors): %d' % (translated, skipped))
    if translated > 0:
        print('Auto-translated strings are marked with: %s' % AUTO_TRANSLATE_COMMENT)


if __name__ == '__main__':
    main()

"""Compare the submitted PDF to the round-four marked PDF. Requires PyMuPDF."""
import argparse
import difflib
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import pymupdf

REVISION_COLORS = {0x7030A0, 0x0070C0, 0xC00000, 0x00B050}
# Ranges in PDF points measured against the two submitted layouts. Existing
# floats are compared independently of where TeX placed them in the text flow.
# Names use round-four numbering. A missing original region denotes a new figure.
REGIONS = {
    'Table 3': ((14, 40, 78, 203), (14, 40, 78, 202)),
    'Table 4': ((15, 40, 78, 269), (16, 40, 78, 269)),
    'Table 5': ((17, 40, 78, 214), (18, 40, 78, 214)),
    'Figure 4': (None, (17, 40, 78, 170)),
    'Figure 5': ((16, 40, 575, 658), (17, 40, 575, 658)),
    'Figure 6': ((17, 244, 337, 475), (18, 244, 296, 425)),
    'Figure 7': ((18, 40, 230, 411), (20, 40, 75, 254)),
    'Figure 8': ((18, 244, 499, 617), (20, 244, 277, 391)),
    'Figure 9': ((19, 244, 157, 274), (21, 244, 102, 218)),
}


def read_regions(pdf, revised):
    streams = defaultdict(list)
    bibliography = False
    with pymupdf.open(pdf) as doc:
        for page in doc:
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    selected = []
                    for span in line['spans']:
                        x, y, _, _ = span['bbox']
                        text = span['text']
                        if y < 74 or y > 667 or (x < 35 and text.strip().isdecimal()):
                            continue
                        if revised and span['color'] in REVISION_COLORS:
                            continue
                        selected.append(span)
                    if not selected:
                        continue
                    text = ''.join(s['text'] for s in selected).strip()
                    if not text:
                        continue
                    if text == 'References':
                        bibliography = True
                    region = 'References' if bibliography else 'Body'
                    x, y, x1, y1 = line['bbox']
                    for name, pair in REGIONS.items():
                        box = pair[int(revised)]
                        if box and page.number + 1 == box[0] and x >= box[1] and box[2] <= (y+y1)/2 <= box[3]:
                            region = name
                            break
                    streams[region].append(text)
    return streams


def words(lines):
    raw = unicodedata.normalize('NFKC', '\n'.join(lines))
    raw = raw.replace('\u00ad', '').replace('−', '-')
    raw = re.sub(r'(?<=[a-zA-Z])-\s*\n\s*(?=[a-zA-Z])', '', raw)
    # A word such as 'one-time' may be broken at its lexical hyphen in just one copy.
    raw = re.sub(r'(?<=[a-zA-Z])-(?=[a-zA-Z])', '', raw)
    return re.findall(r"[^\W_]+|[^\s\w]", raw)


def body_words(lines, revised):
    text = ' '.join(words(lines))
    text = re.sub(r'(?<=cost)(?=Tblock\b)', ' ', text)
    text = re.sub(r'\b(?:23|25) pages \.', 'PAGES pages .', text)
    # Map original labels onto the final identifiers; preserve all empirical numbers.
    if not revised:
        text = re.sub(r'\bFig \. ([4-8])\b', lambda m: 'Fig . '+str(int(m[1])+1), text)
    def citation(match):
        values = [int(n) for n in re.findall(r'\d+', match[1])]
        if not revised:
            values = [{44: 46, 45: 48}.get(n, n) for n in values]
        return '[ '+', '.join(map(str,values))+' ]'
    text = re.sub(r'\[ ([0-9 ,]+) \]', citation, text)
    return text.split()


def compare(original, marked, output, normalized_body=False):
    source, revision = read_regions(original, False), read_regions(marked, True)
    regions = ['Body'] if normalized_body else ['Body', *REGIONS, 'References']
    with output.open('w', encoding='utf-8') as out:
        out.write('region\told_token\tnew_token\tleft_context\toriginal\trevised\tright_context\n')
        for region in regions:
            if normalized_body:
                a, b = body_words(source[region], False), body_words(revision[region], True)
            else:
                a, b = words(source[region]), words(revision[region])
            for kind, i, j, k, l in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
                if kind != 'equal':
                    row = [region, str(i), str(k), ' '.join(a[max(i-4,0):i]), ' '.join(a[i:j]),
                           ' '.join(b[k:l]), ' '.join(b[l:l+4])]
                    out.write('\t'.join(row[:-1] + [row[-1] or '∅'])+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('original', 'marked', 'output'):
        parser.add_argument(arg, type=Path)
    parser.add_argument('--normalized-body', action='store_true')
    args = parser.parse_args()
    compare(args.original, args.marked, args.output, args.normalized_body)

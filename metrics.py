"""Transparent lexical scoring; no semantic or numeral normalization."""
import re

def normalize(text):
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)*", text.lower().replace('’', "'"))

def edit_distance(a, b):
    row = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        nxt = [i]
        for j, right in enumerate(b, 1):
            nxt.append(min(nxt[-1]+1, row[j]+1, row[j-1]+(left != right)))
        row = nxt
    return row[-1]

def errors(row):
    return edit_distance(normalize(row['reference']), normalize(row['text']))

def summarize(rows):
    if not rows or any(not normalize(r['reference']) for r in rows):
        raise ValueError('Nonempty rows and reference words are required')
    words = sum(len(normalize(r['reference'])) for r in rows)
    edits = sum(errors(r) for r in rows)
    return {'n': len(rows), 'reference_words': words, 'word_errors': edits,
            'wer': edits/words,
            'exact_match_rate': sum(normalize(r['reference']) == normalize(r['text']) for r in rows)/len(rows)}

def paired_changes(rows, condition):
    groups = {}
    for r in rows:
        group=groups.setdefault(r['sample_id'], {})
        if r['condition'] in group:
            raise ValueError('Duplicate sample-condition pair')
        group[r['condition']] = r
    out = {'improved':0,'worsened':0,'unchanged':0}
    for group in groups.values():
        if 'none' not in group or condition not in group:
            raise ValueError('Missing paired condition')
        if group['none']['reference'] != group[condition]['reference']:
            raise ValueError('Paired references differ')
        delta = errors(group[condition])-errors(group['none'])
        out['improved' if delta < 0 else 'worsened' if delta > 0 else 'unchanged'] += 1
    return out

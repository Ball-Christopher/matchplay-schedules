import re, json, sys
V = None  # vacancy marker
def parse(path):
    secs, cur = [], None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('## '):
            cur = {'title': line[3:].strip(), 'weeks': [], 'pattern': [], 'k': None, 'text': ''}
            secs.append(cur); continue
        if cur is None: continue
        m = re.match(r'^\|\s*(\d+)\s*\|(.*)\|\s*$', line)
        m2 = re.match(r'^(\d+)\.\s+(.*?)\s*\|?\s*$', line)
        cells = None
        if m:
            cells = [c.strip() for c in m.group(2).split('|')]
        elif m2 and '|' in line:
            cells = [c.strip() for c in m2.group(2).split('|') if c.strip()]
        else:
            if not line.startswith('|'): cur['text'] += line + ' '
            continue
        pat = None
        if cells and re.fullmatch(r'\d+', cells[0]) and len(cells) > 1 and ' ' not in cells[0] and not any(' ' not in c and c for c in cells[1:2]) is False:
            pass
        groups = []
        for c in cells:
            toks = c.replace('—', ' 0 ').split()
            groups.append([int(t) for t in toks])
        if len(groups[0]) == 1 and len(groups) > 1 and len(groups[1]) > 1:
            pat = groups[0][0]; groups = groups[1:]
        cur['weeks'].append(groups); cur['pattern'].append(pat)
    return [s for s in secs if s['weeks']]

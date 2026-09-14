import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data/content-overrides.json';o=json.loads(p.read_text());words={r['word'] for r in json.loads((ROOT/'data/prepared.json').read_text())}
for line in (ROOT/'data/word-relations.txt').read_text().splitlines():
    if not line.strip():continue
    w,s,a=line.split('|');assert w in words,w
    d=o.setdefault(w,{})
    d['synonyms']=[x.strip() for x in s.split(',') if x.strip()];d['antonyms']=[x.strip() for x in a.split(',') if x.strip()]
p.write_text(json.dumps(o,ensure_ascii=False,indent=2))

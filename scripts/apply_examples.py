import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data/content-overrides.json';o=json.loads(p.read_text())
for line in (ROOT/'data/short-examples.txt').read_text().splitlines():
    if not line.strip():continue
    w,k,e=line.split('|',2);o.setdefault(w,{}).setdefault('examples',{})[k]=e
p.write_text(json.dumps(o,ensure_ascii=False,indent=2))

"""Update display content only. The source archive and progress are never replaced."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import connect
from import_data import build
rows=json.loads((ROOT/'data/prepared.json').read_text());o=json.loads((ROOT/'data/content-overrides.json').read_text());cards,merges,missing=build(rows,o)
assert not missing
with connect(ROOT/'data/flashcards.sqlite3') as db:
    for c in cards:
        result=db.execute('UPDATE cards SET type=?,pronunciation=?,content=? WHERE id=? AND word=?',(c['type'],c['pronunciation'],json.dumps(c['content'],ensure_ascii=False),c['id'],c['word']))
        assert result.rowcount==1
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
p=ROOT/'reports/import-verification.json';report=json.loads(p.read_text());report.update(display_meanings=sum(len(c['content']['meanings']) for c in cards),merged_groups=len(merges),senses_without_examples=len(missing));p.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

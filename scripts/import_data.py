"""Import the audited preparation into SQLite, preserving source bytes and cell text."""
import hashlib,json,re,sys,sqlite3
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app import connect
from lemminflect import getInflection

def strip_label(s):return re.sub(r'^\([A-Z /-]+\)\s*','',s)
def role(s):
    s=strip_label(s).lower()
    if s.startswith('to '):return 'verb'
    if re.match(r'(a |an |the act |someone |a person |something that |the process )',s):return 'noun'
    return 'other'
def groups_for(row):
    groups=[]
    for i,d in enumerate(row['definitions']):
        found=False
        for g in groups:
            if all(row['similarities'][i][j]>=.78 and not ({role(d),role(row['definitions'][j])}=={'verb','noun'}) for j in g):
                g.append(i);found=True;break
        if not found:groups.append([i])
    return groups

def short_example(text):
    # Remove dictionary glosses, never cut sentences or strip arbitrary clauses.
    text=re.sub(r'\s*\(=[^)]*\)','',text)
    text=re.sub(r'\s+',' ',text).strip()
    return text

def build(rows,overrides):
    cards=[];merges=[];missing=[]
    for row in rows:
        override=overrides.get(row['word'],{})
        groups=[[i-1 for i in g] for g in override.get('groups',[])] or groups_for(row)
        assert sorted(i for g in groups for i in g)==list(range(len(row['definitions']))),row['word']
        senses=[]
        for g in groups:
            key=str(min(g)+1)
            # Longest original wording keeps qualifications and embedded sub-senses.
            representative=max(g,key=lambda i:len(row['definitions'][i]))
            meaning=override.get('meanings',{}).get(key,row['definitions'][representative])
            meaning=re.sub(r'([a-z])([A-Z])',r'\1. \2',meaning)
            meaning=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]','',meaning)
            for broken,fixed in {'keptthe money':'kept; the money','writingsomething':'writing; something','weaponto manage':'weapon; to manage','officeto put':'office; to put','ojects':'objects'}.items():meaning=meaning.replace(broken,fixed)
            examples=[short_example(e['text']) for e in row['examples'] if e['definition']-1 in g]
            example=override.get('examples',{}).get(key,min(examples,key=lambda e:len(e.split())) if examples else '')
            senses.append({'text':meaning,'example':example,'source_definitions':[i+1 for i in g]})
            if len(g)>1:merges.append({'word':row['word'],'definitions':[i+1 for i in g],'retained':meaning})
            if not example:missing.append({'word':row['word'],'key':key,'meaning':meaning})
        typ=override.get('type',row['type'] or 'ADJECTIVE')
        if any(role(d)=='verb' for d in row['definitions']) and 'VERB' not in typ.split(' · ') and typ != 'PHRASAL VERB' and not override.get('no_inferred_verb'):typ+=' · VERB'
        if any(role(d)=='noun' for d in row['definitions']) and typ in ('VERB','PHRASAL VERB'):typ+=' · NOUN'
        forms={};inflections=[]
        if 'VERB' in typ.split(' · ') or 'PHRASAL VERB' in typ.split(' · '):
            w=override.get('verb_base',row['word']);past=getInflection(w,tag='VBD');part=getInflection(w,tag='VBN')
            forms={'Present':w,'Past':past[0] if past else '', 'Future':'will '+w,'Past participle':part[0] if part else ''}
            forms.update(override.get('forms',{}))
            assert all(forms.values()),f'Missing forms: {w}'
            inflections=list(dict.fromkeys(v for tag in ('VBD','VBN','VBG','VBZ') for v in getInflection(w,tag=tag)))
        synonyms=list(dict.fromkeys(override.get('synonyms',row['synonyms'])))[:3]
        antonyms=list(dict.fromkeys(override.get('antonyms',row['antonyms'])))[:3]
        content=dict(meanings=senses,synonyms=synonyms,antonyms=antonyms,forms=forms,inflections=inflections,original_ids=[row['id']])
        cards.append(dict(id=row['id'],word=row['word'],type=typ,pronunciation=row['pronunciation'],content=content))
    return cards,merges,missing

def main():
    source=ROOT.parent/'Words_With_Examples.html'
    rows=json.loads((ROOT/'data/prepared.json').read_text())
    overrides=json.loads((ROOT/'data/content-overrides.json').read_text())
    cards,merges,missing=build(rows,overrides)
    (ROOT/'reports/merged-definitions.json').write_text(json.dumps(merges,ensure_ascii=False,indent=2))
    (ROOT/'reports/missing-examples.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2))
    if '--preview' in sys.argv:
        (ROOT/'reports/cards-preview.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2));print(f'{len(cards)} cards, {len(merges)} merged groups, {len(missing)} senses without examples');return
    raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    with connect(ROOT/'data/flashcards.sqlite3') as db:
        db.executescript((ROOT/'schema.sql').read_text())
        if db.execute('SELECT count(*) FROM events').fetchone()[0]:raise RuntimeError('Study history exists. Import only into a pristine database.')
        if db.execute('SELECT count(*) FROM sources').fetchone()[0]:raise RuntimeError('Source already imported; refusing to overwrite the archive.')
        sid=db.execute('INSERT INTO sources(name,sha256,html,imported_at) VALUES(?,?,?,?)',(source.name,sha,raw,datetime.now(timezone.utc).isoformat())).lastrowid
        for row,card in zip(rows,cards):
            db.execute('INSERT INTO originals VALUES(?,?,?,?,?)',(row['id'],sid,row['id'],json.dumps(row['cells'],ensure_ascii=False),row['row_html']))
            db.execute('INSERT INTO cards VALUES(?,?,?,?,?)',(card['id'],card['word'],card['type'],card['pronunciation'],json.dumps(card['content'],ensure_ascii=False)))
        assert db.execute('SELECT count(*) FROM originals').fetchone()[0]==len(rows)
        assert db.execute('SELECT html FROM sources').fetchone()[0]==raw
        for row in rows:assert json.loads(db.execute('SELECT cells_json FROM originals WHERE id=?',(row['id'],)).fetchone()[0])==row['cells']
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    report={'original_rows':len(rows),'cards':len(cards),'original_definitions':sum(len(r['definitions']) for r in rows),'display_meanings':sum(len(c['content']['meanings']) for c in cards),'merged_groups':len(merges),'senses_without_examples':len(missing),'source_sha256':sha,'source_bytes':len(raw),'original_fields_verified':len(rows)*7,'archive_byte_verified':True}
    (ROOT/'reports/import-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()

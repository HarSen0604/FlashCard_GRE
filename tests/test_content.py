import hashlib,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import connect,create_app

@pytest.fixture(scope='module')
def data():
    with connect(ROOT/'data/seed.sqlite3') as db:
        return {r['word']:{**dict(r),'content':json.loads(r['content'])} for r in db.execute('SELECT * FROM cards')}

def test_complete_lossless_archive():
    with connect(ROOT/'data/seed.sqlite3') as db:
        source=db.execute('SELECT * FROM sources').fetchone()
        assert hashlib.sha256(source['html']).hexdigest()==source['sha256']
        assert len(source['html'])==772213
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(source['html'],'html.parser');trs=soup.select('tbody tr')
        assert len(trs)==995==db.execute('SELECT count(*) FROM originals').fetchone()[0]
        for i,tr in enumerate(trs,1):
            cells=[]
            for td in tr.find_all('td',recursive=False):
                for br in td.find_all('br'):br.replace_with('\n')
                cells.append(td.get_text().strip())
            assert cells==json.loads(db.execute('SELECT cells_json FROM originals WHERE id=?',(i,)).fetchone()[0])
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()

def test_all_cards_content_invariants(data):
    prepared={r['word']:r for r in json.loads((ROOT/'data/prepared.json').read_text())}
    assert len(data)==995
    for w,c in data.items():
        x=c['content'];assert c['type'] and c['pronunciation'],w
        assert x['meanings'],w
        assert sorted(i for d in x['meanings'] for i in d['source_definitions'])==list(range(1,len(prepared[w]['definitions'])+1)),w
        assert len(x['synonyms'])<=3 and len(x['antonyms'])<=3,w
        assert len(set(x['synonyms']))==len(x['synonyms']),w
        assert not set(x['synonyms']).intersection(x['antonyms']),w
        assert all(d['text'].strip() and d['example'].strip() for d in x['meanings']),w
        assert all(len(d['example'].split())<=27 for d in x['meanings']),w
        is_verb='VERB' in c['type'].split(' · ') or 'PHRASAL VERB' in c['type'].split(' · ')
        assert bool(x['forms'])==is_verb,w
        if is_verb:assert set(x['forms'])=={'Present','Past','Future','Past participle'} and all(x['forms'].values()),w

def test_adverbs_and_adjectives_do_not_get_fake_tenses(data):
    for w in ['abreast','conversely','hotly','likewise','moreover','nevertheless','respectively','searchingly','mired','predisposed','conversant','partial','umbrage']:
        assert not data[w]['content']['forms'],w

@pytest.mark.parametrize('w,past,part',[('bent','bent','bent'),('gainsay','gainsaid','gainsaid'),('hew','hewed','hewn'),('rend','rent','rent'),('offset','offset','offset'),('steeped','steeped','steeped'),('succeeding','succeeded','succeeded')])
def test_irregular_and_inflected_headwords(data,w,past,part):
    f=data[w]['content']['forms'];assert f['Past']==past and f['Past participle']==part

def test_gre_sense_distinctions(data):
    for w,terms in {'qualified':['training','reservations'],'sanction':['penalty','permission'],'abridge':['writing','rights'],'grouse':['bird','excellent'],'secrete':['liquid','found']}.items():
        joined=' '.join(d['text'].lower() for d in data[w]['content']['meanings'])
        assert all(t in joined for t in terms),(w,joined)
    assert len(data['loquacious']['content']['meanings'])==1
    assert len(data['abate']['content']['meanings'])==1
    assert 'impartial' in data['disinterested']['content']['synonyms']
    assert 'discerning' in data['discriminating']['content']['synonyms']

def test_sqlite_only_startup(tmp_path,monkeypatch):
    # Copy only SQLite into a directory containing no source/preparation files.
    import shutil
    path=tmp_path/'independent.sqlite3';shutil.copy2(ROOT/'data/seed.sqlite3',path);monkeypatch.chdir(tmp_path)
    app=create_app(path);c=app.test_client()
    assert c.get('/api/status').json['total']==995
    assert c.get('/').status_code==200
    assert c.post('/api/start',json={'count':2},headers={'X-FlashCard':'1'}).status_code==200
    card=c.post('/api/next',json={'mode':'learn'},headers={'X-FlashCard':'1'}).json['card']
    assert c.get('/api/original/'+str(card['id'])).json

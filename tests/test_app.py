import json,sqlite3,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import create_app,connect

@pytest.fixture
def env(tmp_path):
    tick=[1800000000.0]
    app=create_app(tmp_path/'test.sqlite3',lambda:tick[0]);app.config['TESTING']=True
    with connect(app.config['DATABASE']) as db:
        for i in range(1,7):db.execute('INSERT INTO cards VALUES(?,?,?,?,?)',(i,f'word{i}','NOUN','/test/',json.dumps({'meanings':[{'text':'test','example':'A test.'}],'synonyms':[],'antonyms':[],'forms':{},'original_ids':[]})))
    return app,app.test_client(),tick

def post(client,path,data=None):return client.post('/api/'+path,json=data or {},headers={'X-FlashCard':'1'})
def start(c,n=3):assert post(c,'start',{'count':n}).status_code==200

def next_card(c,mode='learn',card_id=None):
    d={'mode':mode}
    if card_id:d['card_id']=card_id
    return post(c,'next',d).get_json()

def rate(c,p,r='easy'):
    assert post(c,'flip',{'token':p['token']}).status_code==200
    return post(c,'rate',{'token':p['token'],'rating':r})

def graduate(c,tick,n=3):
    start(c,n);seen=[]
    for _ in range(n*5+5):
        p=next_card(c)
        if p.get('wait_seconds'):tick[0]+=31;continue
        if p.get('done'):break
        seen.append(p['card']['id']);assert rate(c,p).status_code==200
        tick[0]+=1
    assert c.get('/api/status').json['learned']==n
    return seen

def test_random_unique_and_active_block(env):
    app,c,t=env;start(c,6)
    with connect(app.config['DATABASE']) as db:
        assert db.execute('SELECT count(distinct card_id) FROM members').fetchone()[0]==6
    assert post(c,'start',{'count':1}).status_code==409
    assert c.get('/api/status').json['learned']==0

@pytest.mark.parametrize('n',[0,-1,1.5,'3',True,7,None])
def test_invalid_size(env,n):
    _,c,_=env;assert post(c,'start',{'count':n}).status_code==400
    assert c.get('/api/status').json['batch'] is None

def test_flip_and_duplicate_submission(env):
    _,c,_=env;start(c);p=next_card(c)
    assert post(c,'rate',{'token':p['token'],'rating':'easy'}).status_code==409
    assert rate(c,p).status_code==200
    assert post(c,'rate',{'token':p['token'],'rating':'easy'}).status_code==409
    assert c.get('/api/status').json['learning_attempts']==1

def test_session_survives_restart(env):
    app,c,t=env;start(c);p=next_card(c);rate(c,p,'good')
    new_app=create_app(app.config['DATABASE'],lambda:t[0]);new_c=new_app.test_client()
    assert new_c.get('/api/status').json['batch']['size']==3
    assert new_c.get('/api/status').json['learning_attempts']==1
    assert next_card(new_c)['card']['id']!=p['card']['id']

def test_singleton_cooldown_and_reset(env):
    _,c,t=env;start(c,1)
    for i in range(2):
        p=next_card(c);assert p['streak']==i;rate(c,p,'good')
        assert next_card(c)['wait_seconds']>=30;t[0]+=31
    p=next_card(c);assert p['streak']==2;rate(c,p,'again');t[0]+=31
    p=next_card(c);assert p['streak']==0
    for _ in range(3):rate(c,p,'good');t[0]+=31;p=next_card(c)
    assert p['streak']==3 and p['status']['learned']==0
    rate(c,p,'easy');assert c.get('/api/status').json['learned']==1

def test_interleaved_three_recalls_and_atomic_graduation(env):
    _,c,t=env;seen=graduate(c,t,3)
    assert len(seen)==9
    assert all(a!=b for a,b in zip(seen,seen[1:]))
    s=c.get('/api/status').json
    assert s['learning_attempts']==9 and s['revision_attempts']==0 and s['batch'] is None
    start(c,3)
    with connect(env[0].config['DATABASE']) as db:assert db.execute('SELECT count(distinct card_id) FROM members').fetchone()[0]==6

def test_ready_member_stays_out_of_library_until_all_ready(env):
    app,c,t=env;start(c,2)
    first=next_card(c)['card']['id']
    for _ in range(6):
        p=next_card(c);rate(c,p,'easy' if p['card']['id']==first else 'again');t[0]+=1
    s=c.get('/api/status').json;assert s['batch']['ready']==1 and s['learned']==0
    assert c.get('/api/library').json==[]
    assert post(c,'next',{'mode':'review','card_id':first}).status_code==409

def test_revision_due_early_and_separate_counts(env):
    _,c,t=env;graduate(c,t,2);s=c.get('/api/status').json
    assert s['due']==0
    assert next_card(c,'review')['done']
    rows=c.get('/api/library').json;card_id=rows[0]['id']
    p=next_card(c,'review',card_id);rate(c,p,'again')
    with connect(env[0].config['DATABASE']) as db:
        e=db.execute("SELECT * FROM events WHERE mode='review'").fetchone();assert e['early']==1
        schedule=db.execute('SELECT * FROM schedules WHERE card_id=?',(card_id,)).fetchone()
        assert 500<schedule['due']-t[0]<700
    s=c.get('/api/status').json;assert s['revision_attempts']==1 and s['learning_attempts']==6 and s['learned']==2
    t[0]+=601;assert next_card(c,'review')['card']['id']==card_id
    rate(c,next_card(c,'review'),'easy');assert c.get('/api/status').json['revision_attempts']==2

def test_undo_graduation_restores_entire_batch(env):
    _,c,t=env;graduate(c,t,2)
    p=post(c,'undo').json
    assert p['status']['learned']==0 and p['status']['batch']['ready']==1
    assert p['status']['learning_attempts']==5
    rate(c,p,'again');assert c.get('/api/status').json['batch']['ready']==1
    assert next_card(c).get('wait_seconds')

def test_undo_revision_restores_due_and_history(env):
    _,c,t=env;graduate(c,t,1);before=c.get('/api/library').json
    p=next_card(c,'review',before[0]['id']);rate(c,p,'again');post(c,'undo')
    assert c.get('/api/library').json==before
    assert c.get('/api/status').json['revision_attempts']==0
    assert post(c,'undo').status_code==409

def test_stale_token_and_security(env):
    _,c,_=env;start(c);p=next_card(c)
    assert post(c,'flip',{'token':'bad'}).status_code==409
    assert c.post('/api/start',json={'count':1}).status_code==403
    assert c.get('/api/status',headers={'Host':'evil.example'}).status_code==403
    assert post(c,'rate',{'token':p['token'],'rating':'bad'}).status_code==400
    assert next_card(c)['token']==p['token']

def test_backup_valid_and_contains_progress(env,tmp_path):
    _,c,_=env;start(c);rate(c,next_card(c))
    response=c.get('/api/backup');assert response.status_code==200
    path=tmp_path/'backup.sqlite3';path.write_bytes(response.data)
    with sqlite3.connect(path) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert db.execute('SELECT count(*) FROM events').fetchone()[0]==1

def test_exhaustion_and_filters(env):
    _,c,t=env;graduate(c,t,6)
    assert c.get('/api/status').json['new']==0
    assert post(c,'start',{'count':1}).status_code==400
    assert len(c.get('/api/library?q=word1').json)==1
    assert not c.get('/api/library?filter=due').json
    assert not c.get('/api/library?filter=again').json

@pytest.mark.parametrize('body',[[],[1],None,'hello',123])
def test_bad_json_shapes(env,body):
    _,c,_=env
    assert c.post('/api/start',data=json.dumps(body),content_type='application/json',headers={'X-FlashCard':'1'}).status_code==400

def test_huge_batch_request_is_rejected_cleanly(env):
    _,c,_=env
    assert post(c,'start',{'count':10**100}).status_code==400

def test_batch_continues_across_days(env):
    app,c,t=env;start(c,2);p=next_card(c);rate(c,p,'good');t[0]+=86400*3
    fresh=create_app(app.config['DATABASE'],lambda:t[0]).test_client()
    assert fresh.get('/api/status').json['batch']['turn']==1
    assert fresh.get('/api/status').json['learned']==0
    assert next_card(fresh)['card']['id']!=p['card']['id']

def test_concurrent_duplicate_rating_counts_once(env):
    from concurrent.futures import ThreadPoolExecutor
    app,c,t=env;start(c);p=next_card(c);post(c,'flip',{'token':p['token']})
    def send():
        with app.test_client() as client:return post(client,'rate',{'token':p['token'],'rating':'easy'}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:send(),range(2)))
    assert sorted(results)==[200,409]
    assert c.get('/api/status').json['learning_attempts']==1

def test_revision_during_active_batch_does_not_graduate_new_words(env):
    _,c,t=env;graduate(c,t,2);start(c,2);before=c.get('/api/status').json
    word=c.get('/api/library').json[0]['id'];p=next_card(c,'review',word);rate(c,p,'easy')
    after=c.get('/api/status').json
    assert after['batch']==before['batch'] and after['learned']==2
    assert after['revision_attempts']==1
    assert next_card(c)['mode']=='learn'

def test_replace_presentation_rejects_other_tabs_token(env):
    _,c,t=env;graduate(c,t,2);start(c,2);p=next_card(c)
    word=c.get('/api/library').json[0]['id'];other=next_card(c,'review',word)
    assert post(c,'flip',{'token':p['token']}).status_code==409
    assert rate(c,other).status_code==200

def test_review_all_order_once_resume_undo_and_dates(env):
    app,c,t=env;graduate(c,t,3)
    with connect(app.config['DATABASE']) as db:
        ids=[r[0] for r in db.execute('SELECT card_id FROM schedules ORDER BY card_id')]
        for card_id,offset in zip(ids,[86400,-100,3600]):db.execute('UPDATE schedules SET due=? WHERE card_id=?',(t[0]+offset,card_id))
    expected=[ids[1],ids[2],ids[0]]
    assert post(c,'review-all').status_code==200
    first=next_card(c,'review-all');assert first['card']['id']==expected[0]
    assert first['due']==t[0]-100
    result=rate(c,first,'again').json
    assert result['next_due']==t[0]+600
    with connect(app.config['DATABASE']) as db:
        assert db.execute('SELECT due FROM schedules WHERE card_id=?',(expected[0],)).fetchone()[0]==result['next_due']
    undone=post(c,'undo').json
    assert undone['due']==t[0]-100 and undone['review_queue']['completed']==0
    assert undone['mode']=='review-all'
    rate(c,undone,'good')
    fresh=create_app(app.config['DATABASE'],lambda:t[0]).test_client()
    post(fresh,'review-all')
    for position,card_id in enumerate(expected[1:],1):
        card=next_card(fresh,'review-all')
        assert card['card']['id']==card_id
        assert card['review_queue']=={'total':3,'completed':position}
        assert next_card(fresh,'review-all')['token']==card['token']
        assert rate(fresh,card,'easy').status_code==200
    assert next_card(fresh,'review-all')['done']
    assert c.get('/api/status').json['revision_attempts']==3
    post(c,'review-all');assert next_card(c,'review-all')['review_queue']['completed']==0

def test_review_all_empty_and_mode_switch(env):
    _,c,t=env;post(c,'review-all');assert next_card(c,'review-all')['done']
    graduate(c,t,2);post(c,'review-all');p=next_card(c,'review-all')
    other=next_card(c,'review',p['card']['id'])
    assert post(c,'flip',{'token':p['token']}).status_code==409
    rate(c,other)
    post(c,'review-all');resumed=next_card(c,'review-all')
    assert resumed['card']['id']==p['card']['id']
    assert resumed['review_queue']['completed']==0

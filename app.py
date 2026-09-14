"""Local, single-user GRE study app. All durable state lives in SQLite."""
import io,json,os,secrets,sqlite3,time
from datetime import datetime,timezone,timedelta
from pathlib import Path
from flask import Flask,request,jsonify,render_template,send_file
from fsrs import Scheduler,Card,Rating

ROOT=Path(__file__).resolve().parent
RATINGS={'again':Rating.Again,'good':Rating.Good,'easy':Rating.Easy}
PROGRESS=('batches','members','schedules','events','presentation')

def connect(path):
    db=sqlite3.connect(path,timeout=15)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db

def create_app(database=None,clock=None):
    app=Flask(__name__)
    app.config.update(DATABASE=str(database or ROOT/'data/flashcards.sqlite3'),MAX_CONTENT_LENGTH=16384)
    now=clock or time.time
    scheduler=Scheduler(desired_retention=.9,learning_steps=(),relearning_steps=(timedelta(minutes=10),),enable_fuzzing=False)
    Path(app.config['DATABASE']).parent.mkdir(parents=True,exist_ok=True)
    if database is None and not Path(app.config['DATABASE']).exists():
        with sqlite3.connect(ROOT/'data/seed.sqlite3') as source,sqlite3.connect(app.config['DATABASE']) as target:source.backup(target)
    with connect(app.config['DATABASE']) as db:db.executescript((ROOT/'schema.sql').read_text())
    def state(db):
        active=db.execute('SELECT * FROM batches WHERE completed_at IS NULL').fetchone()
        total=db.execute('SELECT count(*) FROM cards').fetchone()[0]
        learned=db.execute('SELECT count(*) FROM schedules').fetchone()[0]
        reserved=db.execute('SELECT count(*) FROM members').fetchone()[0]
        counts=dict(db.execute('SELECT mode,count(*) FROM events GROUP BY mode').fetchall())
        batch=None
        if active:
            batch=dict(active)
            batch.update(dict(db.execute('SELECT count(*) size,coalesce(sum(ready),0) ready FROM members WHERE batch_id=?',(active['id'],)).fetchone()))
        return dict(total=total,learned=learned,new=total-reserved,due=db.execute('SELECT count(*) FROM schedules WHERE due<=?',(now(),)).fetchone()[0],batch=batch,learning_attempts=counts.get('learn',0),revision_attempts=counts.get('review',0),undo=bool(db.execute('SELECT 1 FROM actions WHERE undone=0 ORDER BY id DESC LIMIT 1').fetchone()))
    def payload(db,p):
        card=dict(db.execute('SELECT * FROM cards WHERE id=?',(p['card_id'],)).fetchone())
        card['content']=json.loads(card['content'])
        member=db.execute('SELECT streak,ready FROM members WHERE card_id=?',(p['card_id'],)).fetchone()
        return dict(card=card,token=p['token'],revealed=bool(p['revealed']),mode=p['mode'],streak=member['streak'] if member else 0,status=state(db))
    def snapshot(db):return json.dumps({t:[dict(r) for r in db.execute('SELECT * FROM '+t)] for t in PROGRESS})
    def fail(msg,code=400):return jsonify(error=msg),code
    @app.before_request
    def local_only():
        if request.host.split(':')[0] not in ('127.0.0.1','localhost','[::1]'):return fail('Use the local application address.',403)
        if request.method=='POST':
            if request.headers.get('X-FlashCard')!='1':return fail('Invalid application request.',403)
            if not isinstance(request.get_json(silent=True),dict):return fail('Expected a JSON object.')
    @app.after_request
    def headers(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'"
        return response
    @app.get('/')
    def index():return render_template('index.html')
    @app.get('/api/status')
    def status():
        with connect(app.config['DATABASE']) as db:return jsonify(state(db))
    @app.post('/api/start')
    def start():
        data=request.get_json(silent=True) or {};n=data.get('count')
        if type(n)!=int or n<1:return fail('Enter a whole number of at least 1.')
        with connect(app.config['DATABASE']) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM batches WHERE completed_at IS NULL').fetchone():return fail('Resume your unfinished batch before starting another.',409)
            available=db.execute('SELECT count(*) FROM cards WHERE id NOT IN (SELECT card_id FROM members)').fetchone()[0]
            if n>available:return fail(f'Only {available} new words are available.')
            ids=[r[0] for r in db.execute('SELECT id FROM cards WHERE id NOT IN (SELECT card_id FROM members) ORDER BY random() LIMIT ?',(n,))]
            if len(ids)!=n:return fail(f'Only {len(ids)} new words are available.')
            bid=db.execute('INSERT INTO batches(created_at) VALUES(?)',(now(),)).lastrowid
            db.executemany('INSERT INTO members(batch_id,card_id,position,due_turn) VALUES(?,?,?,?)',[(bid,c,i,i) for i,c in enumerate(ids)])
            db.execute('DELETE FROM presentation');db.execute('UPDATE actions SET undone=1')
            return jsonify(state(db))
    @app.post('/api/next')
    def next_card():
        data=request.get_json(silent=True) or {};mode=data.get('mode','learn');chosen=data.get('card_id')
        if mode not in ('learn','review'):return fail('Unknown study mode.')
        with connect(app.config['DATABASE']) as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT * FROM presentation').fetchone()
            if old and old['mode']==mode and (chosen is None or chosen==old['card_id']):return jsonify(payload(db,old))
            card_id=None
            if mode=='learn':
                batch=db.execute('SELECT * FROM batches WHERE completed_at IS NULL').fetchone()
                if not batch:return jsonify(done=True,status=state(db))
                pending=db.execute('SELECT * FROM members WHERE batch_id=? AND ready=0 ORDER BY due_turn,position',(batch['id'],)).fetchall()
                alternatives=[r for r in pending if r['card_id']!=batch['last_card']]
                if alternatives:card_id=alternatives[0]['card_id']
                elif pending:
                    remaining=30-(now()-(batch['last_at'] or 0))
                    if remaining>0:return jsonify(wait_seconds=int(remaining)+1,status=state(db))
                    card_id=pending[0]['card_id']
            elif chosen is not None:
                if type(chosen)!=int:return fail('Invalid card.')
                if not db.execute('SELECT 1 FROM schedules WHERE card_id=?',(chosen,)).fetchone():return fail('This word has not completed initial learning.',409)
                card_id=chosen
            else:
                row=db.execute('SELECT card_id FROM schedules WHERE due<=? ORDER BY due,card_id LIMIT 1',(now(),)).fetchone()
                if row:card_id=row[0]
            if card_id is None:
                upcoming=db.execute('SELECT min(due) FROM schedules').fetchone()[0]
                return jsonify(done=True,next_due=upcoming,status=state(db))
            db.execute('DELETE FROM presentation')
            db.execute('INSERT INTO presentation VALUES(1,?,?,?,0)',(secrets.token_urlsafe(24),card_id,mode))
            return jsonify(payload(db,db.execute('SELECT * FROM presentation').fetchone()))
    @app.post('/api/flip')
    def flip():
        data=request.get_json(silent=True) or {}
        with connect(app.config['DATABASE']) as db:
            result=db.execute('UPDATE presentation SET revealed=1 WHERE token=?',(data.get('token'),))
            if result.rowcount!=1:return fail('This card changed in another tab. Reload the study session.',409)
        return jsonify(ok=True)
    @app.post('/api/rate')
    def rate():
        data=request.get_json(silent=True) or {};rating=data.get('rating');token=data.get('token')
        if rating not in RATINGS:return fail('Choose one of the three confidence ratings.')
        with connect(app.config['DATABASE']) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM actions WHERE token=?',(token,)).fetchone():return fail('This rating has already been submitted.',409)
            p=db.execute('SELECT * FROM presentation WHERE token=?',(token,)).fetchone()
            if not p:return fail('This card changed in another tab. Reload the study session.',409)
            if not p['revealed']:return fail('Reveal the answer before rating it.',409)
            before=snapshot(db);timestamp=now();dt=datetime.fromtimestamp(timestamp,timezone.utc);early=0;log=None;graduated=False
            if p['mode']=='learn':
                m=db.execute('SELECT * FROM members WHERE card_id=?',(p['card_id'],)).fetchone()
                streak=0 if rating=='again' else min(3,m['streak']+1)
                ready=int(streak>=3 and rating=='easy')
                batch=db.execute('SELECT * FROM batches WHERE id=?',(m['batch_id'],)).fetchone()
                turn=batch['turn']+1
                db.execute('UPDATE members SET streak=?,ready=?,due_turn=? WHERE card_id=?',(streak,ready,turn+{'again':1,'good':3,'easy':5}[rating],p['card_id']))
                db.execute('UPDATE batches SET turn=?,last_card=?,last_at=? WHERE id=?',(turn,p['card_id'],timestamp,batch['id']))
                if db.execute('SELECT count(*) FROM members WHERE batch_id=? AND ready=0',(batch['id'],)).fetchone()[0]==0:
                    for member in db.execute('SELECT card_id FROM members WHERE batch_id=?',(batch['id'],)).fetchall():
                        card,_=scheduler.review_card(Card(),Rating.Good,dt)
                        db.execute('INSERT INTO schedules(card_id,state,due) VALUES(?,?,?)',(member[0],card.to_json(),card.due.timestamp()))
                    db.execute('UPDATE batches SET completed_at=? WHERE id=?',(timestamp,batch['id']));graduated=True
            else:
                row=db.execute('SELECT * FROM schedules WHERE card_id=?',(p['card_id'],)).fetchone()
                early=int(row['due']>timestamp)
                card,review=scheduler.review_card(Card.from_json(row['state']),RATINGS[rating],dt)
                log=review.to_json()
                db.execute('UPDATE schedules SET state=?,due=?,last_rating=?,reviews=reviews+1 WHERE card_id=?',(card.to_json(),card.due.timestamp(),rating,p['card_id']))
            db.execute('INSERT INTO events(card_id,mode,rating,created_at,early,fsrs_log) VALUES(?,?,?,?,?,?)',(p['card_id'],p['mode'],rating,timestamp,early,log))
            db.execute('INSERT INTO actions(token,snapshot) VALUES(?,?)',(token,before))
            # One-step undo only; avoid accumulating copies of all history.
            db.execute('DELETE FROM actions WHERE id NOT IN (SELECT max(id) FROM actions)')
            db.execute('DELETE FROM presentation')
            return jsonify(graduated=graduated,status=state(db))
    @app.post('/api/undo')
    def undo():
        with connect(app.config['DATABASE']) as db:
            db.execute('BEGIN IMMEDIATE')
            action=db.execute('SELECT * FROM actions WHERE undone=0 ORDER BY id DESC LIMIT 1').fetchone()
            if not action:return fail('There is no rating to undo.',409)
            saved=json.loads(action['snapshot'])
            for table in reversed(PROGRESS):db.execute('DELETE FROM '+table)
            for table in PROGRESS:
                for row in saved[table]:db.execute('INSERT INTO '+table+' ('+','.join(row)+') VALUES ('+','.join('?' for _ in row)+')',tuple(row.values()))
            # Fresh token allows a corrected rating while rejecting the old request.
            db.execute('UPDATE presentation SET token=?',(secrets.token_urlsafe(24),))
            db.execute('UPDATE actions SET undone=1 WHERE id=?',(action['id'],))
            return jsonify(payload(db,db.execute('SELECT * FROM presentation').fetchone()))
    @app.get('/api/library')
    def library():
        query=request.args.get('q','').strip().lower();kind=request.args.get('filter','all')
        with connect(app.config['DATABASE']) as db:
            rows=db.execute('SELECT c.id,c.word,c.type,s.due,s.last_rating,s.reviews FROM schedules s JOIN cards c ON c.id=s.card_id ORDER BY s.due,c.word').fetchall()
            return jsonify([dict(r) for r in rows if query in r['word'].lower() and (kind=='all' or (kind=='due' and r['due']<=now()) or r['last_rating']==kind)])
    @app.get('/api/original/<int:card_id>')
    def original(card_id):
        with connect(app.config['DATABASE']) as db:
            row=db.execute('SELECT content FROM cards WHERE id=?',(card_id,)).fetchone()
            if not row:return fail('Word not found.',404)
            ids=json.loads(row[0])['original_ids']
            return jsonify([json.loads(db.execute('SELECT cells_json FROM originals WHERE id=?',(i,)).fetchone()[0]) for i in ids])
    @app.get('/api/backup')
    def backup():
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            dest=Path(directory)/'flashcards.sqlite3'
            with connect(app.config['DATABASE']) as source,sqlite3.connect(dest) as target:source.backup(target)
            return send_file(io.BytesIO(dest.read_bytes()),as_attachment=True,download_name='flashcards-backup.sqlite3',mimetype='application/vnd.sqlite3')
    return app

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=5055);parser.add_argument('--database');args=parser.parse_args()
    create_app(args.database).run(host='127.0.0.1',port=args.port,debug=False)

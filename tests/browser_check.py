"""Real Chromium tests against an isolated copy of the delivered database."""
import json,os,shutil,socket,sqlite3,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def run():
    with tempfile.TemporaryDirectory(prefix='wordwell-test-') as directory:
        dbpath=Path(directory)/'test.sqlite3';shutil.copy2(ROOT/'data/seed.sqlite3',dbpath)
        sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
        log=open(ROOT/'reports/browser-server.log','w')
        proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--database',str(dbpath),'--port',str(port)],cwd=directory,stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                try:urllib.request.urlopen(f'http://127.0.0.1:{port}/api/status');break
                except Exception:time.sleep(.1)
            else:raise RuntimeError('Test server did not start')
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
                page=browser.new_page(viewport={'width':1440,'height':1000})
                errors=[];external=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:external.append(r.url) if not r.url.startswith(f'http://127.0.0.1:{port}') and not r.url.startswith('data:') else None)
                page.goto(f'http://127.0.0.1:{port}');page.wait_for_function("() => document.querySelector('#metric-new').textContent === '995'")
                page.screenshot(path=str(ROOT/'reports/home-desktop.png'),full_page=True)
                page.locator('#count').fill('3');page.get_by_role('button',name='Start learning').click();page.locator('#word').wait_for(state='visible')
                first=page.locator('#word').inner_text();page.reload();page.get_by_role('button',name='Resume learning').click();page.locator('#word').wait_for(state='visible');assert page.locator('#word').inner_text()==first
                page.screenshot(path=str(ROOT/'reports/card-front-desktop.png'),full_page=True)
                # Real user journey: flip, inspect archive, rate, undo, finish entire batch.
                page.locator('#flip').click();page.locator('#back').wait_for(state='visible');page.locator('#original-details summary').click();page.wait_for_function("() => document.querySelector('#original-text').textContent.length > 0");page.locator('#original-details summary').click()
                page.locator('[data-rating=good]').click();page.locator('#front').wait_for(state='visible');page.locator('#undo').click();page.wait_for_function('() => !busy');page.locator('#front').wait_for(state='visible');assert page.locator('#word').inner_text()==first
                assert page.locator('#streak-text').inner_text()=='0 / 3 consecutive recalls'
                seen=[]
                for i in range(9):
                    page.locator('#front').wait_for(state='visible');seen.append(page.locator('#word').inner_text());page.locator('#flip').click();page.locator('#back').wait_for(state='visible')
                    if i==0:page.screenshot(path=str(ROOT/'reports/card-back-desktop.png'),full_page=True)
                    page.locator('[data-rating=easy]').click()
                page.get_by_role('heading',name='Your batch is ready for revision.').wait_for();assert all(a!=b for a,b in zip(seen,seen[1:]))
                assert page.request.get(f'http://127.0.0.1:{port}/api/status').json()['learned']==3
                page.locator('#tab-library').click();page.wait_for_function("() => document.querySelectorAll('.library-row').length===3")
                page.locator('.library-row button').first.click();page.locator('#flip').click();page.locator('[data-rating=again]').click();page.get_by_role('heading',name='You’re up to date.').wait_for()
                assert page.request.get(f'http://127.0.0.1:{port}/api/status').json()['revision_attempts']==1
                page.locator('#tab-library').click();page.locator('#filter').select_option('again');page.wait_for_function("() => document.querySelectorAll('.library-row').length===1")
                page.screenshot(path=str(ROOT/'reports/library-desktop.png'),full_page=True)
                # Audit every front/back using real rendering functions and database content.
                with sqlite3.connect(dbpath) as db:
                    db.row_factory=sqlite3.Row;cards=[dict(r) for r in db.execute('SELECT * FROM cards')]
                for c in cards:c['content']=json.loads(c['content'])
                checks=[]
                for width,height in [(1440,1000),(1280,800),(768,1024),(390,844)]:
                    page.set_viewport_size({'width':width,'height':height})
                    result=page.evaluate('''cards => {
                        const problems=[];let scrollCards=0;
                        const s={total:995,new:992,learned:3,due:0,learning_attempts:9,revision_attempts:1,batch:{size:3,ready:0},undo:false};
                        for(const card of cards){
                            renderCard({card,token:'layout-test',mode:'learn',streak:0,status:s});
                            for(const flipped of [false,true]){
                                setFlipped(flipped);
                                const root=document.querySelector('#card');
                                if(!flipped && window.innerWidth>=801 && window.innerHeight>=800 && document.querySelector('#flip').getBoundingClientRect().bottom>window.innerHeight)problems.push([card.word,'reveal below fold']);
                                if(root.scrollWidth>root.clientWidth+1)problems.push([card.word,flipped,'horizontal card overflow']);
                                if(document.documentElement.scrollWidth>window.innerWidth+1)problems.push([card.word,flipped,'page overflow']);
                                for(const n of root.querySelectorAll('*')){
                                    if(n.getClientRects().length && n.textContent.trim() && parseFloat(getComputedStyle(n).fontSize)<16)problems.push([card.word,'small font']);
                                }
                                if(flipped&&root.scrollHeight>root.clientHeight+1)scrollCards++;
                            }
                        }
                        return {problems,scrollCards,cards:cards.length};
                    }''',cards)
                    checks.append({'viewport':[width,height],**result});assert not result['problems'],result['problems'][:10]
                # Longest card + mobile screenshots and bottom-content reachability.
                longest=max(cards,key=lambda c:len(c['content']['meanings']))
                page.evaluate("c => renderCard({card:c,token:'layout',mode:'learn',streak:0,status:{total:995,new:992,learned:3,due:0,learning_attempts:9,revision_attempts:1,batch:{size:3,ready:0},undo:false}})",longest)
                page.evaluate('() => setFlipped(true)');page.screenshot(path=str(ROOT/'reports/long-card-mobile.png'),full_page=True)
                page.locator('#card').evaluate('(n)=>n.scrollTop=n.scrollHeight')
                assert page.locator('#original-details summary').is_visible()
                page.set_viewport_size({'width':1280,'height':800});page.locator('#card').evaluate('(n)=>n.scrollTop=0');page.screenshot(path=str(ROOT/'reports/long-card-laptop.png'),full_page=True)
                assert not errors,errors
                assert not external,external
                browser.close()
                report={'journey':'passed','all_card_layout_checks':checks,'javascript_errors':errors,'external_requests':external,'production_progress_untouched':True}
                (ROOT/'reports/browser-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
        finally:
            proc.terminate();proc.wait(timeout=10);log.close()
if __name__=='__main__':run()

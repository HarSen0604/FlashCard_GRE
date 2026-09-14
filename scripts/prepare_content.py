"""One-time semantic preparation; app runtime never loads this model or the HTML."""
import json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HOME',str(ROOT/'data/model-cache'))
os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
from bs4 import BeautifulSoup
from lemminflect import getInflection

def clean(s):return re.sub(r'\s+',' ',s).strip().rstrip(':').strip()
def extract(path):
    soup=BeautifulSoup(Path(path).read_bytes(),'html.parser');rows=[]
    for tr in soup.select('tbody tr'):
        tds=tr.find_all('td',recursive=False)
        if not tds:continue
        assert len(tds)==7
        cells=[]
        for td in tds:
            copy=BeautifulSoup(str(td),'html.parser')
            for br in copy.find_all('br'):br.replace_with('\n')
            cells.append(copy.get_text().strip())
        word=clean(cells[2].splitlines()[0]);pron=' '.join(cells[2].splitlines()[1:]).strip()
        definitions=[clean(s) for s in re.split(r'(?:^|\n)\s*\d+\.\s*',cells[3]) if clean(s)]
        examples=[]
        for num,txt in re.findall(r'\[Def\s+(\d+)\]\s*(.*?)(?=\[Def\s+\d+\]|$)',cells[6],re.S):examples.append({'definition':int(num),'text':clean(txt)})
        rows.append(dict(id=len(rows)+1,word=word,type=cells[1].strip(),pronunciation=pron,definitions=definitions,examples=examples,synonyms=[clean(s) for s in cells[4].splitlines() if clean(s)],antonyms=[clean(s) for s in cells[5].splitlines() if clean(s)],cells=cells,row_html=str(tr)))
    return rows

def main():
    from sentence_transformers import SentenceTransformer
    import numpy as np
    source=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'Words_With_Examples.html'
    rows=extract(source)
    model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2',cache_folder=str(ROOT/'data/model-cache'),device='cpu')
    texts=[re.sub(r'^\([A-Z /-]+\)\s*','',d) for r in rows for d in r['definitions']]
    embeddings=model.encode(texts,batch_size=64,normalize_embeddings=True,show_progress_bar=True)
    offset=0;pairs=[]
    for row in rows:
        n=len(row['definitions']);e=embeddings[offset:offset+n];offset+=n
        row['similarities']=(e@e.T).tolist()
        for i in range(n):
            for j in range(i+1,n):
                score=row['similarities'][i][j]
                if score>=.75:pairs.append(dict(word=row['word'],a=i+1,b=j+1,score=round(score,3),first=row['definitions'][i],second=row['definitions'][j]))
        if row['type'] in ('VERB','PHRASAL VERB'):
            word=row['word'];past=getInflection(word,tag='VBD');part=getInflection(word,tag='VBN')
            row['forms']={'Present':word,'Past':past[0] if past else '', 'Future':'will '+word,'Past participle':part[0] if part else ''}
            row['inflections']=list(dict.fromkeys([v for tag in ('VBD','VBN','VBG','VBZ') for v in getInflection(word,tag=tag)]))
        else:row['forms']={};row['inflections']=[]
    (ROOT/'data/prepared.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    (ROOT/'reports/similarity-candidates.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2))
    print(f'{len(rows)} rows; {len(texts)} definitions; {len(pairs)} semantic pairs >= .75',flush=True)
if __name__=='__main__':main()

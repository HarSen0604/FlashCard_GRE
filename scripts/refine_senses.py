"""Editorial review of paraphrases missed by the similarity model."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'data/content-overrides.json';o=json.loads(p.read_text());cards=json.loads((ROOT/'reports/cards-preview.json').read_text())
# Separate literal/figurative senses, different grammatical uses, and specific terms.
keep=set('abyss advocate aesthetic amortize apostle brook bygone canonical catholic clamber cloying coda complementary constrict covert craven demur desiccate deterrent din distaff doff dovetail egalitarian eminent expedient facilitate fathom finesse ford gestation glower gradation harangue harrow impute incendiary itinerant kindle lampoon libertine livid lurid maelstrom mar mendicant mercurial mitigate nettle nontrivial orotund ossify paradigm parley parry pedestrian penitent perennial phalanx pious plutocracy polarized polyglot prattle profound puissance repose ridden rue ruminate sanguine savor secrete squalid stint toady tangential unsparing untempered wan whet zenith'.split())
count=0
for c in cards:
    m=c['content']['meanings']
    if len(m)!=2 or c['word'] in keep:continue
    ids=sorted(i for sense in m for i in sense['source_definitions']);key=str(ids[0]);d=o.setdefault(c['word'],{})
    d['groups']=[ids];d.setdefault('meanings',{})[key]=max(m,key=lambda s:len(s['text']))['text']
    example=min((s['example'] for s in m if s['example']),key=len)
    d.setdefault('examples',{}).setdefault(key,example);count+=1
# Explicitly preserve multiple embedded senses when simplifying broken source markup.
fix={
'myopic':'Unable to see distant objects clearly; also, unable to consider the future consequences of a situation or action.',
'prologue':'An introductory part of a play, story, or poem; also, events that precede and lead to a main event.',
'rhetoric':'Speech or writing intended to persuade; the art or study of using language effectively; also, impressive language lacking sincerity or substance.',
'vanguard':'The leading part of an advancing military force; also, people leading new ideas or developments.',
'winnow':'To separate chaff from grain using air; also, to select a smaller group by judging quality.',
'monastic':'Connected with monks or monasteries; also, a simple, secluded way of life with few possessions.',
'steeped':'Past tense and past participle of steep: kept in liquid to soften, clean, or develop flavor; also, deeply filled with an influence, quality, or tradition.',
'conversant':'Familiar with or knowledgeable about the facts, rules, or practice of something.',
'quixotic':'Admirably idealistic but impractical or unlikely to succeed.',
'facilitate':'To make something possible or easier.',
}
for w,t in fix.items():o.setdefault(w,{}).setdefault('meanings',{})['1']=t
# More than two paraphrases of the same sense.
rows={r['word']:r for r in json.loads((ROOT/'data/prepared.json').read_text())}
for w in ['abridge','qualified','loquacious','bolster','grouse','stigma','strut','lumber']:
 r=rows[w]
 if w=='abridge':groups=[[1,3],[2]]
 elif w=='qualified':groups=[[1,3,4],[2]]
 elif w=='loquacious':groups=[[1,2]]
 elif w=='bolster':groups=[[1,3],[2,4]]
 elif w=='grouse':groups=[[1,6],[2],[3,5],[4]]
 elif w=='stigma':groups=[[1,3],[2,4]]
 elif w=='strut':groups=[[1,3],[2,4]]
 elif w=='lumber':groups=[[1,4],[2,3,5]]
 if sorted(i for g in groups for i in g)==list(range(1,len(r['definitions'])+1)):
  o.setdefault(w,{})['groups']=groups
# Qualified must preserve the often-tested limited/reserved sense.
o['qualified'].setdefault('meanings',{})['1']='Having the training, skills, knowledge, or ability needed for something.'
o['qualified']['meanings']['2']='Limited or subject to reservations; not complete or unconditional.'
o['qualified'].setdefault('examples',{})['2']='She gave qualified approval, insisting on further checks.'
o['winnow'].setdefault('examples',{})['1']='The committee winnowed fifty applications down to five.'
# Remove the cross-reference once synonymous lumber definitions are combined.
o.setdefault('lumber',{}).setdefault('meanings',{})['2']='Wood cut and prepared for building; timber.'
p.write_text(json.dumps(o,ensure_ascii=False,indent=2));print(f'Editorially merged {count} pairs of overlapping meanings.')

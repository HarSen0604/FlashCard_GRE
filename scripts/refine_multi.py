"""Reviewed grouping for remaining multi-sense entries; preserve every source index."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'data/content-overrides.json';o=json.loads(p.read_text());rows={r['word']:r for r in json.loads((ROOT/'data/prepared.json').read_text())}
# Semicolon separates distinct display meanings; commas mark overlapping originals.
spec='''
abdicate|1,2,3
abrasive|1,5;2,4;3
abscond|1;2,3
abstain|1,2,4;3
adverse|1,2,3
anoint|1,2,3
antedate|1,2,3
appropriate|1,4;2,5;3
arbiter|1,2,3,4
articulate|1,5;2,6;3;4
ascetic|1,3;2
ascribe|1,2,3,4
august|1,4;2,3
balloon|1,4;2,5,8;3;6,7
benign|1,2,3
bent|1,6;2;3,8;4;5,7
blight|1,3;2
bogus|1,2,3
buffer|1,6,7;2;3;4,9;5,8
bureaucracy|1,3;2,4
buttress|1,4;2,3
catalyst|1,2,3
caustic|1,2,3
censure|1,2,4,5;3
clamor|1,2,3
clinch|1,5;2,4;3
coffer|1,3,4;2
concede|1,4,5,7;2,6;3
concur|1,2,3
confer|1,3,5;2,4
console|1,4,5;2,6;3
consolidate|1,2,3,4;5;6
contrary|1,2,4,5;3,6
converge|1,2,3,4,5
crafty|1,3;2
delineate|1,2,3
derivative|1,5;2,6;3,7;4
detached|1,4;2,3
diffuse|1,4;2,5;3
discredit|1,3;2
discrepancy|1,2,3
disinterested|1,2,4;3
dismiss|1,4,8;2,6;3,5,7
dispatch|1,4,6,7;2;3,5,8
disposition|1,2;3;4
dissent|1,3;2,4
dither|1,2,3
diverge|1,2,3,4
divest|1,2,3
divine|1,5;2,6;3,7;4
document|1,3,5,6;2,4,7
dupe|1,4;2,5;3
eclectic|1,2,3
eclipse|1,5;2;3;4,6,7,8
entitlement|1,3,4;2,5
erratic|1,2,3
exponent|1,3,5,6;2,4,7
fallow|1,3;2,4
feasible|1,2,3
fidelity|1,3,5;2,4
figurative|1,2,3
fledgling|1;2,3,4,5
florid|1,4;2,3
forage|1,3;2
forfeit|1,5,6,7;2;3,4,8
fringe|1,2,7,10;3,8;4;5;6,9
frugal|1,2,3
goad|1,5;2;3;4
gouge|1,4;2,5;3
graft|1,7;2,9;3,6,8;4;5,10
grating|1,4;2,3
grovel|1,2,3
hallmark|1,4,5;2,6;3,7
haven|1,3,4;2
hedge|1,5;2,6,8;3;4,7,9,10
hew|1,2;3
hierarchy|1,2,3,4
husband|1,3;2
impasse|1,2,3
impervious|1;2,3
implicit|1,3;2,4
incorporate|1,3,6;2,4,5
indifferent|1,3;2,4
inert|1,3;2,4
inform|1,2,3,5;4
ingrained|1,3;2
inter|1,3;2,4,5
inundate|1,2,3
keen|1,7,10;2,5,6,8;3;4;9
lament|1,3;2,4
landmark|1,3;2,4,5
liberal|1,7,12;2,8,13,14;3,9,15;4,10,16;5,17;6,11,18
listless|1,2,3
log|1,6;2,7,12;3;4,9;5,8,10,11
lull|1,3;2,4,5
mannered|1,2,3
maverick|1,3,4,5;2
meticulous|1,2,3
modest|1,4,7;2,5;3,6
nominal|1,4,7;2,5,6;3;8
novel|1,3;2,4
objective|1,5,6;2,3,7;4
oblique|1,6;2,5;3;4
occult|1,3;2
offhand|1;2,3,4
offset|1,2,3,4;5;6,7
opaque|1,2,3
optimal|1,2,3
orthodox|1,2,3
oscillate|1,2,3
outstrip|1,2,3,4,5
partial|1,5,7;2;3,6;4
partisan|1,3;2
pathological|1,3;2,4
peddle|1,2,3,4
per|1,2,3;4
peripheral|1,3,5;2,4,6,7
philistine|1,3;2
phony|1,2;3
plastic|1,6;2,8;3;4;5,7
plummet|1,2,3;4
precipitate|1,6;2;3,7;4,8;5
prodigal|1,3;2
profligate|1,3;2
prohibitive|1,2,3;4
propagate|1,2,4;3
propensity|1,2,3
prospective|1,2,3,4
proxy|1,2,3,4,5;6
prudent|1,2,3;4
quibble|1,3;2
rarefied|1;2,3
reap|1,2,3,4
redress|1,3,4,5;2,6
remedial|1,3;2
render|1,4,7;2,5,6,8;3;9;10;11
repertory|1,2,3
reproach|1,3;2
repudiate|1,2,3,4
resolution|1,8,9;2;3,7,10;4,11;5;6
retrospective|1;2,3,4
revamp|1,3,4;2,5
sap|1,4;2,5;3,6
saturate|1,2,4,5;3
skirt|1,6;2;3;4;5,7
spearhead|1,3,5;2,4
spectrum|1,4;2,3,5
speculate|1,3,5;2,4,6
squelch|1;2,4;3
stark|1,3;2
static|1,3,4;2
stoic|1,3;2
subpoena|1,3,4,5;2,6;7
subside|1,3;2,4
succeeding|1,2,3
supersede|1,2,3,4
surmise|1,3;2
tawdry|1,3;2
terrestrial|1,2,4;3,5
torrid|1,4;2,3;5;6
treacherous|1,3;2,4
turgid|1,4;2;3,5
unearth|1,2,3
vacillate|1,2,4;3
via|1,2,3
vintage|1,5;2,7,8;3,9;4,6
virtual|1,3,4;2,5
virulent|1,2,3
volatile|1,2,3,4
wanton|1,3;2
whitewash|1,2,7;3;4;5;6
yoke|1,3,7;2;4;5;6
'''
for line in spec.strip().splitlines():
 w,g=line.split('|');groups=[[int(i) for i in group.split(',')] for group in g.split(';')]
 assert sorted(i for group in groups for i in group)==list(range(1,len(rows[w]['definitions'])+1)),w
 d=o.setdefault(w,{})
 # Existing overridden meanings inside a new group can have unique information;
 # choose the most complete current/original wording unless explicitly revised below.
 for group in groups:
  options=[d.get('meanings',{}).get(str(i),rows[w]['definitions'][i-1]) for i in group]
  d.setdefault('meanings',{})[str(min(group))]=max(options,key=len)
 d['groups']=groups
fix={
'abdicate':{1:'To give up a throne or position of authority; also, to fail to take responsibility for something.'},
'abstain':{1:'To deliberately refrain from an activity, especially something enjoyable or unhealthy; also, to choose not to vote.'},
'anoint':{1:'To put holy water or oil on someone in a religious ceremony, including when making someone king or queen; also, to choose someone for a job or purpose.'},
'arbiter':{1:'Someone who makes judgments, settles disputes, or decides what is acceptable; also, someone whose opinion strongly influences others.'},
'ascribe':{1:'To attribute a cause, authorship, ownership, or characteristic to someone or something.'},
'balloon':{6:'A loan repaid in small installments followed by a much larger final payment; also, that final payment.'},
'benign':{1:'Kind, gentle, or harmless; of a growth or tumor, not cancerous.'},
'catalyst':{1:'A substance that speeds a chemical reaction without being consumed overall; also, a person or event that brings about significant change.'},
'caustic':{1:'Able to burn or corrode substances, especially living tissue; of words, harsh, biting, or hurtfully critical.'},
'console':{2:'A panel or device with controls for electronic equipment or a vehicle; also, a games machine or a cabinet containing electronic equipment.'},
'consolidate':{1:'To make stronger or more secure; to combine separate things, businesses, or amounts into a more effective whole.'},
'converge':{1:'To move toward the same point and meet; also, to become more similar or join together, as with opinions, prices, economies, or products.'},
'dispatch':{3:'The act of sending; also, a report or official message sent from elsewhere. Mentioned in dispatches means praised for military service; with dispatch means quickly.'},
'figurative':{1:'Of language, using words imaginatively rather than literally; of art, representing recognizable real objects rather than abstract forms.'},
'forfeit':{1:'To lose or give up a right, possession, or opportunity, especially for breaking a rule or failing an obligation.'},
'grovel':{1:'To lie or move close to the ground, especially in fear; also, to behave with excessive humility to win favor.'},
'hedge':{2:'A barrier or safeguard against risk; in finance, an investment intended to reduce losses.',4:'To limit or protect against risk; also, to avoid a direct answer or firm commitment.'},
'keen':{2:'Strong or intense, as with feelings or competition; sharp or well-developed, as with awareness or intellect; of wind, strong and cold.'},
'liberal':{2:'Supporting personal freedom and social reform, often including a fairer distribution of wealth and public services; in economic usage, favoring business freedom and limited government interference.',6:'A supporter of liberal political or economic beliefs, including social reform and personal freedom, or free enterprise and limited government interference.'},
'log':{3:'Short for logarithm: the power to which a base must be raised to obtain a given number.',5:'To record officially; also, to accumulate a recorded distance, time, or number of achievements.'},
'mannered':{1:'Having a specified way of behaving, as in well-mannered; also, artificial or affected in speech, behavior, or style.'},
'peripheral':{1:'At or near an edge; also, secondary or less important. Peripheral vision is what you see to the sides of your direct gaze.'},
'prospective':{1:'Expected or possible in the future, as with a customer, parent, employee, cost, or profit.'},
'proxy':{1:'A person or thing acting in place of another; also, authority or a document allowing someone to act or vote for you, or the vote itself. In computing, an intermediary server that processes exchanges between users and other servers.'},
'reap':{1:'To cut and collect a crop; also, to obtain rewards, advantages, or profits as a result of actions or circumstances.'},
'render':{2:'To give or provide something, such as a service, opinion, or performance; also, to represent something in art or performance.'},
'repudiate':{1:'To refuse to accept or recognize something; also, to reject an agreement or refuse to repay a debt.'},
'saturate':{1:'To soak completely or fill to capacity; in chemistry, to combine with as much of another substance as possible; in a market, to supply more than buyers want.'},
'succeeding':{1:'Present participle of succeed: achieving a desired result; following something in time; or taking over a position after someone else.'},
'vintage':{2:'Of lasting high quality or characteristic excellence, especially something old; also, used but still of good quality.'},
'virulent':{1:'Of a disease or poison, dangerous and fast-acting or rapidly spreading; also, fiercely hostile or hateful.'},
'volatile':{1:'Likely to change suddenly or become angry or violent; of a substance, readily changing into gas.'},
'whitewash':{1:'A white coating made from lime or chalk and water; figuratively, an attempt to conceal wrongdoing.'},
'yoke':{1:'A wooden bar linking draft animals to a load; figuratively, a burden or connection that unfairly restricts freedom.'}
}
for w,definitions in fix.items():o.setdefault(w,{}).setdefault('meanings',{}).update({str(i):text for i,text in definitions.items()})
# Correct source example labels that do not illustrate the displayed sense.
examples={
'hand':{1:'She held the small stone in her hand.'},
'spectrum':{1:'A prism separates white light into a spectrum of colors.',2:'The debate covered a broad spectrum of political opinions.'},
'abdicate':{1:'The king abdicated and passed the throne to his daughter.'},
'arbiter':{1:'Both sides accepted her as the final arbiter of the dispute.'},
'ascribe':{1:"She ascribed the project's success to careful planning."},
'catalyst':{1:'The discovery became a catalyst for rapid scientific progress.'},
'caustic':{1:'His caustic remarks embarrassed the speaker.'},
'consolidate':{1:'The firms consolidated their separate teams into one stronger unit.'},
'converge':{1:'The two roads converge at the bridge.'},
'dispatch':{3:'The correspondent sent a dispatch describing the battle.'},
'proxy':{1:'She voted by proxy while traveling abroad.'},
'log':{3:'The log to base ten of one hundred is two.'},
'prospective':{1:'The school welcomed prospective students to its open day.'},
'saturate':{1:'Heavy rain saturated the dry soil.'},
'volatile':{1:'His volatile temper made disagreements unpredictable.'},
'yoke':{1:'The oxen pulled together beneath a wooden yoke.'}
}
for w,es in examples.items():o.setdefault(w,{}).setdefault('examples',{}).update({str(i):e for i,e in es.items()})
p.write_text(json.dumps(o,ensure_ascii=False,indent=2));print('Multi-sense editorial review applied.')

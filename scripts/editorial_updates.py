"""Explicit sense-preserving editorial decisions for overloaded dictionary entries."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'data/content-overrides.json'
o=json.loads(P.read_text())
def edit(w,groups=None,meanings=None,**kw):
    d=o.setdefault(w,{})
    if groups:d['groups']=groups
    if meanings:d.setdefault('meanings',{}).update({str(k):v for k,v in meanings.items()})
    d.update(kw)
edit('advocate',[[1,3,4],[2,5,6]])
edit('aggregate',[[1,3,5,7,10,11],[2,9],[4,6,12],[8],[13]],{1:'(NOUN / ADJECTIVE) A total formed by adding several amounts or things; total or combined. In sport, on aggregate means across two or more matches.'},type='NOUN · ADJECTIVE · VERB')
edit('base',[[1,11],[2,3,12,20],[4,18],[5,6,16,21],[7],[8,14],[9],[10,19,24],[13],[15],[17],[22],[23]],{2:'The main place where a person lives or works, or a company operates; a military base houses personnel, buildings, and weapons.',5:'The main part of something, or the people, activities, and resources it depends on for support or success.',8:'(CHEMISTRY) A substance that reacts with an acid to form a salt; many bases dissolve in water.'},type='NOUN · ADJECTIVE · VERB')
edit('default',[[1,6,13,14],[2],[3,5,8,11,12],[4,7,9,10],[15]],{1:'To fail to do something required by law or agreement, such as repay a debt.',3:'The standard setting or result that applies unless someone makes a different choice. In sport, winning by default means the opponent did not play, finish, or follow the rules.',4:'Failure to meet a legal or contractual obligation, such as paying a debt; in sport, failure to compete.'},type='VERB · NOUN · ADJECTIVE')
edit('e',[[1,9],[2,10],[3],[4,6,11,13],[5],[7,8,12]])
edit('flag',[[1,9,15],[2],[3],[4],[5,10,12,13,16],[6],[7,11,14],[8],[17]],{3:'A flat stone used for paving; a flagstone.',4:'A type of iris flower.',5:'(VERB / NOUN) To mark something for attention or later processing; the mark itself. In computing, a flag can indicate one of two possible values.',17:'(FLY THE FLAG) To show support for your country, group, or organization.'})
edit('hand',[[1,12],[2,13],[3,14],[4,24],[5,15],[6,16,19],[7],[8,17],[9],[10],[11,18],[20],[21,25],[22],[23],[26],[27,31],[28],[29],[30]],{11:'To pass something from your hand to another person; in some sports, to touch the ball or puck illegally with the hand.',20:'(HAND IN HAND) Happening together or working closely together.',21:'(IN HAND) Available, or currently being dealt with.',22:'(BY HAND) Made or done using hands rather than a machine; delivered personally.',23:'(GET YOUR HANDS ON) To find or obtain someone or something you want.',26:'(IN SOMEONE’S HANDS) Being dealt with, controlled, or owned by a particular person or group.',27:'(ON HAND / TO HAND) Nearby and available to help or be used.',28:'(OUT OF YOUR HANDS) No longer under your control or your responsibility.',29:'(PUT YOUR HAND IN YOUR POCKET) To give money to someone or a charity.',30:'(AT HAND) The job or subject needing attention now.'})
edit('net',[[1,8],[2],[3,7,13,23,24],[4,10,18],[5],[6,9,14,19,21,22],[11],[12,16,17],[15],[20]],{3:'The internet; .net is an internet domain originally associated with networks.',4:'To catch something using a net; to obtain something valuable or earn money.',6:'(NOUN / ADJECTIVE / ADVERB) What remains after deductions such as costs, tax, or packaging weight; the overall result after relevant additions and subtractions, as in net force.',11:'In sport, to hit a ball into the net instead of over it; also, to catch something in a net.',12:'To earn or have left an amount of money after costs and taxes.',15:'(CAST YOUR NET WIDE) To include many people or possibilities in a search.',20:'(NET EXPORTER) Describes a country that sells or exports more of something than it buys or imports.'},type='NOUN · VERB · ADJECTIVE · ADVERB')
edit('patent',[[1,6,8],[2],[3,11],[4,7],[5,12],[9],[10]],{2:'(PATENT LEATHER) Leather with a smooth, shiny surface.',5:'Protected by a patent, giving the holder exclusive rights for a limited time.',9:'(OFF PATENT) No longer protected because the patent has expired.',10:'(PATENT PENDING) A patent has been requested but has not yet been granted.'},type='NOUN · VERB · ADJECTIVE')
edit('sanction',[[1,6,8,9],[2,5,10],[3,7,11],[4,12]],{1:'An official penalty or restrictive action to enforce a law or rule, including limits on trade with a country.'})
edit('slack',[[1,3,7,9],[2,8,10,11],[4],[5],[6,13],[12],[14],[15]],{1:'Loose or not tight; the looseness in something such as a rope.',2:'Showing little activity; a period when business or work is slower than usual.',6:'To work slowly or with too little effort; also describes someone who does so.',15:'(TAKE UP THE SLACK) To do necessary work that someone else has stopped doing.'},type='ADJECTIVE · NOUN · VERB')
edit('sound',[[1,12],[2,4,14],[3,13],[5,15],[6],[7,16,19],[8,17,18],[9,11],[10],[20]],{2:'To seem a particular way from what is said, written, or heard; the impression this creates.',7:'Healthy, undamaged, or in good condition; financially strong. Also used for deep, peaceful sleep.',8:'Based on good judgment or correct methods; trustworthy, capable, or acceptable.',9:'(SLEEP) Deep or deeply, as in sound sleep or sound asleep.'},type='NOUN · VERB · ADJECTIVE · ADVERB')
edit('standing',[[1,6,7],[2,8],[3,4,10],[5],[9]],{9:'(IN GOOD STANDING) Having met required official procedures and paid required charges.'},type='NOUN · ADJECTIVE')
edit('status',[[1,4,6,8],[2,5,9],[3],[7]],{1:'The accepted, official, legal, or social position of a person or organization; also its state or condition.',2:'The amount of respect or importance someone has; a high social position.'})
edit('table',[[1,6],[2,7,9],[3,8,13,14],[4],[5],[10],[11],[12]],{1:'A flat surface supported by legs for eating or working; also the people sitting there. To set the table means to prepare it for a meal.',2:'An arrangement of facts or numbers in rows and columns, including multiplication tables; a table of contents lists what is in a book.',3:'(VERB) To offer a matter for discussion (especially British usage), or postpone its discussion (especially American usage).',10:'A place or opportunity for discussion or negotiation.',11:'(OFF THE TABLE) No longer being considered.',12:'(ON THE TABLE) Offered for consideration; in some contexts, postponed for later discussion.'})
edit('token',[[1,6,11],[2,7,9,10],[3],[4],[5,8,12,13]],{2:'A voucher, card, electronic document, or disc that can be exchanged for goods or used instead of money; also a collectible promotional coupon.',3:'(COMPUTING) A piece of data used to represent or replace other data, including to protect private information.',5:'Small or limited but symbolic; sometimes done merely to appear supportive or compliant. A token payment is very small.'},type='NOUN · ADJECTIVE')
# Resolve spelling-only and cross-reference entries into usable meanings.
edit('artifact',meanings={1:'An object made by people, especially one of historical or cultural interest.'})
edit('clamor',meanings={1:'A loud, confused noise, or a strong public demand; to make such a noise or demand.'},type='NOUN · VERB')
edit('distill',meanings={1:'To purify a liquid by heating it into vapor and cooling it again; to extract the essential meaning or qualities of something.'},type='VERB')
edit('antedate',meanings={1:'To exist or occur before something else; to give a document a date earlier than its actual date.'})
edit('recapitulate',meanings={1:'To repeat or summarize the main points of something.'})
edit('knell',meanings={1:'The sound of a bell rung for a death; a sign that something is ending or failing.'})
edit('optimal',meanings={2:'Best or most favorable for a particular purpose.'})
edit('molt',[[1,2]],{1:'To lose feathers, skin, or hair as a natural process before new growth.'},type='VERB · NOUN')
edit('baying',meanings={1:'The present participle of bay: making a long, deep cry.',2:'To make a long, deep cry repeatedly, as dogs or wolves do.'},type='VERB',forms={'Present':'bay','Past':'bayed','Future':'will bay','Past participle':'bayed'})
edit('steeped',meanings={1:'Past tense and past participle of steep: soaked in liquid, or deeply filled with a quality, influence, or tradition.'},forms={'Present':'steep','Past':'steeped','Future':'will steep','Past participle':'steeped'})
edit('succeeding',meanings={1:'Present participle of succeed: achieving an aim, or following someone or something.'},forms={'Present':'succeed','Past':'succeeded','Future':'will succeed','Past participle':'succeeded'})
# Clean joined dictionary text without dropping its second sense.
for w,changes in {
'autonomous':{1:'Independent and able to make your own decisions; of an organization or region, self-governing; of a machine or system, able to operate without direct human control.'},
'dyspeptic':{1:'Having difficulty digesting food; also, irritable or easily annoyed.'},
'catalyst':{2:'A condition, event, or person that causes an important change; also, a substance that speeds a chemical reaction without being consumed overall.'},
'partisan':{2:'A member of an armed resistance force fighting an occupying enemy; also, a strong supporter of a person, principle, or political party.'},
'rhetoric':{2:'Effective, persuasive speech or writing; the art or study of speaking and writing effectively.'},
'symbiosis':{1:'A close relationship between organisms; in the mutually beneficial sense used here, each helps the other. Also, a relationship of mutual dependence between people or organizations.'},
 'temperance':{1:'Control of your behavior, especially in eating and drinking; also, abstaining from alcohol.'},
 'torpor':{1:'A state of inactivity and lack of energy or enthusiasm; also a state of reduced activity in some animals.'},
 'unseemly':{1:'Not socially suitable, proper, or polite.'},
 'saturate':{3:'(NOUN) A saturated fat.'},
}.items():edit(w,meanings=changes)
P.write_text(json.dumps(o,ensure_ascii=False,indent=2))

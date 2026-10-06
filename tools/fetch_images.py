import json, os, re, time, urllib.parse, urllib.request
UA={'User-Agent':'art-quiz-personal-study/1.0 (https://github.com/matveykask8er/art-quiz)'}
P=json.load(open('tools/data.json',encoding='utf8'))
os.makedirs('images',exist_ok=True)
mp=json.load(open('images/map.json')) if os.path.exists('images/map.json') else {}
def get(url,binary=False,tries=4):
    for i in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40)
            d=r.read()
            return d if binary else json.loads(d)
        except Exception as e:
            time.sleep(2+i*3)
    return None
def api(host,params):
    return get('https://%s/w/api.php?format=json&%s'%(host,urllib.parse.urlencode(params)))
BAD=re.compile(r'detail|фрагмент|crop|signature|frame|stamp|marka|марка|coin|monument|памятник|статуя|statue|museum|музей|building|здани',re.I)
def commons(q):
    d=api('commons.wikimedia.org',{'action':'query','generator':'search','gsrnamespace':6,'gsrlimit':8,'gsrsearch':q,'prop':'imageinfo','iiprop':'url|mime|size','iiurlwidth':600})
    if not d or 'query' not in d: return None
    pages=sorted(d['query']['pages'].values(),key=lambda x:x.get('index',99))
    for p in pages:
        ii=(p.get('imageinfo') or [{}])[0]
        if not re.match(r'image/(jpeg|png)',ii.get('mime','')): continue
        if BAD.search(p.get('title','')): continue
        if ii.get('width',0)<400: continue
        return ii.get('thumburl') or ii.get('url')
def wiki(host,q):
    d=api(host,{'action':'query','generator':'search','gsrlimit':3,'gsrsearch':q,'prop':'pageimages','piprop':'thumbnail','pithumbsize':600})
    if not d or 'query' not in d: return None
    for p in sorted(d['query']['pages'].values(),key=lambda x:x.get('index',99)):
        t=p.get('thumbnail')
        if t and t.get('source') and not t['source'].lower().endswith('.svg'): return t['source']
missing=[]
for i,p in enumerate(P):
    k=str(i)
    if k in mp and os.path.exists(mp[k]): continue
    title=re.sub(r'\s*\(.*?\)','',p['title']).replace('«','').replace('»','').strip()
    last=p['author'].split(',')[0].split(' ')[-1]
    cands=[]
    if p.get('file'):
        cands.append(lambda f=p['file']:'https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(f)+'?width=600')
    cands+= [lambda:commons(title+' '+last),
             lambda:commons(p['author'].split(',')[0]+' '+title),
             lambda:commons(title+' Google Art Project'),
             lambda:commons(title+' '+p['year'][:4]+' '+last),
             lambda:wiki('ru.wikipedia.org',title+' '+p['author']+' картина'),
             lambda:wiki('en.wikipedia.org',title+' '+p['author']+' painting')]
    ok=False
    for c in cands:
        try: u=c()
        except Exception: u=None
        if not u: continue
        d=get(u,binary=True)
        if d and len(d)>8000 and d[:3] in (b'\xff\xd8\xff',) or (d and d[:4]==b'\x89PNG'):
            ext='jpg' if d[:3]==b'\xff\xd8\xff' else 'png'
            path='images/%d.%s'%(i,ext); open(path,'wb').write(d); mp[k]=path; ok=True; break
        time.sleep(1)
    if not ok: missing.append('%d | %s — %s'%(i,p['author'],p['title']))
    time.sleep(0.7)
json.dump(mp,open('images/map.json','w'))
open('images/MISSING.txt','w',encoding='utf8').write('\n'.join(missing))
print('ok',len(mp),'missing',len(missing))

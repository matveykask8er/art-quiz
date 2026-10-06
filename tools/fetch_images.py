import json, os, re, time, io, urllib.parse, urllib.request
from PIL import Image, ImageStat
UA={'User-Agent':'art-quiz-personal-study/1.0 (https://github.com/matveykask8er/art-quiz)'}
P=json.load(open('tools/data.json',encoding='utf8'))
REDO=set(json.load(open('tools/redo.json'))) if os.path.exists('tools/redo.json') else None
os.makedirs('images',exist_ok=True)
mp=json.load(open('images/map.json')) if os.path.exists('images/map.json') else {}
def get(url,binary=False,tries=4):
    for i in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40)
            d=r.read()
            return d if binary else json.loads(d)
        except Exception:
            time.sleep(2+i*3)
    return None
def api(host,params):
    return get('https://%s/w/api.php?format=json&%s'%(host,urllib.parse.urlencode(params)))
BAD=re.compile(r'detail|фрагмент|crop|signature|frame|stamp|marka|марка|coin|monument|памятник|статуя|statue|museum|музей|building|здани|sketch|эскиз|etude|этюд|drawing|рисунок|study|portrait of the artist|photo|фото|cover|обложк|poster|plakat',re.I)
def commons(q):
    d=api('commons.wikimedia.org',{'action':'query','generator':'search','gsrnamespace':6,'gsrlimit':10,'gsrsearch':q,'prop':'imageinfo','iiprop':'url|mime|size','iiurlwidth':600})
    out=[]
    if not d or 'query' not in d: return out
    for p in sorted(d['query']['pages'].values(),key=lambda x:x.get('index',99)):
        ii=(p.get('imageinfo') or [{}])[0]
        if not re.match(r'image/(jpeg|png)',ii.get('mime','')): continue
        if BAD.search(p.get('title','')): continue
        if ii.get('width',0)<400: continue
        out.append(ii.get('thumburl') or ii.get('url'))
    return out
def wiki(host,q):
    d=api(host,{'action':'query','generator':'search','gsrlimit':3,'gsrsearch':q,'prop':'pageimages','piprop':'thumbnail','pithumbsize':600})
    out=[]
    if not d or 'query' not in d: return out
    for p in sorted(d['query']['pages'].values(),key=lambda x:x.get('index',99)):
        t=p.get('thumbnail')
        if t and t.get('source') and not t['source'].lower().endswith('.svg'): out.append(t['source'])
    return out
def good(d):
    try:
        im=Image.open(io.BytesIO(d)).convert('RGB')
    except Exception: return None
    w,h=im.size
    if w<250 or h<200 and w<400: return None
    hsv=im.resize((80,80)).convert('HSV')
    sat=ImageStat.Stat(hsv).mean[1]/255
    if sat<0.14: return None          # чёрно-белые фото, рисунки, гравюры
    if max(w,h)/min(w,h)>2.6: return None
    return im
def save(im,path):
    im.thumbnail((560,560))
    im.save(path,'JPEG',quality=72,optimize=True)
missing=[]
for i,p in enumerate(P):
    k=str(i)
    if REDO is not None and i not in REDO: continue
    if k in mp and os.path.exists(mp[k]): continue
    title=re.sub(r'\s*\(.*?\)','',p['title']).replace('«','').replace('»','').replace('"','').strip()
    a0=p['author'].split(',')[0]; last=a0.split(' ')[-1]
    qs=[]
    if p.get('file'):
        qs.append(lambda f=p['file']:['https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(f)+'?width=600'])
    qs+=[lambda:commons(title+' '+last),
         lambda:commons(a0+' '+title),
         lambda:commons(title+' Google Art Project'),
         lambda:commons(title+' '+p['year'][:4]+' '+last),
         lambda:commons(last+' '+title+' Третьяковская галерея'),
         lambda:wiki('ru.wikipedia.org',title+' '+a0+' картина'),
         lambda:wiki('en.wikipedia.org',title+' '+a0+' painting')]
    ok=False
    for q in qs:
        try: urls=q()
        except Exception: urls=[]
        for u in urls:
            d=get(u,binary=True)
            if not d: continue
            im=good(d)
            if im is None: continue
            path='images/%d.jpg'%i; save(im,path); mp[k]=path; ok=True; break
            time.sleep(0.5)
        if ok: break
        time.sleep(0.5)
    if not ok: missing.append('%d | %s — %s'%(i,p['author'],p['title']))
    time.sleep(0.5)
json.dump(mp,open('images/map.json','w'))
open('images/MISSING.txt','w',encoding='utf8').write('\n'.join(missing))
print('ok',len(mp),'missing',len(missing))

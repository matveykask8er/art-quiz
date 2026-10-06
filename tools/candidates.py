import json,re,urllib.parse,urllib.request,time
UA={'User-Agent':'art-quiz-personal-study/1.0 (https://github.com/matveykask8er/art-quiz)'}
P=json.load(open('tools/data.json',encoding='utf8')); R=json.load(open('tools/cand_list.json'))
def api(q):
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrlimit':10,'gsrsearch':q,'prop':'imageinfo','iiprop':'size|mime'})
    for t in range(3):
        try:
            d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read())
            out=[]
            for p in sorted(d.get('query',{}).get('pages',{}).values(),key=lambda x:x.get('index',99)):
                ii=(p.get('imageinfo') or [{}])[0]
                if ii.get('mime','').startswith('image/j') or ii.get('mime','').endswith('png'): out.append(p['title'][5:]+' |'+str(ii.get('width'))+'x'+str(ii.get('height')))
            return out
        except Exception: time.sleep(3)
    return []
EXTRA=json.load(open('tools/extra_q.json',encoding='utf8'))
res={}
for i in R:
    p=P[i]; a0=p['author'].split(',')[0]; last=a0.split(' ')[-1]
    title=re.sub(r'\s*\(.*?\)','',p['title']).replace('«','').replace('»','')
    seen=[]
    for q in EXTRA.get(str(i),[])+[title+' '+last, a0+' '+title, title+' Google Art Project', last+' '+p['year'][:4]+' '+title]:
        for t in api(q):
            if t not in seen: seen.append(t)
        time.sleep(0.5)
    res[i]={'who':p['author']+' — '+p['title'],'c':seen}
json.dump(res,open('tools/candidates.json','w'),ensure_ascii=False,indent=1)

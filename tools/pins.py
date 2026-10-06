import json,io,time,urllib.parse,urllib.request
from PIL import Image
UA={'User-Agent':'art-quiz-personal-study/1.0 (https://github.com/matveykask8er/art-quiz)'}
pins=json.load(open('tools/pins.json',encoding='utf8')); mp=json.load(open('images/map.json'))
for k,f in pins.items():
    u='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(f)+'?width=600'
    for t in range(4):
        try:
            d=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
            im=Image.open(io.BytesIO(d)).convert('RGB'); im.thumbnail((560,560)); im.save('images/%s.jpg'%k,'JPEG',quality=72,optimize=True); mp[k]='images/%s.jpg'%k; print('ok',k); break
        except Exception as e:
            print('fail',k,e); time.sleep(3)
json.dump(mp,open('images/map.json','w'))

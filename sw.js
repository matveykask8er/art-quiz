const SHELL='shell-v4', IMG='img-v1';
self.addEventListener('install',e=>{e.waitUntil(caches.open(SHELL).then(c=>c.addAll(['./','index.html','manifest.json','icon-180.png'])).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim());});
self.addEventListener('fetch',e=>{
  const req=e.request; if(req.method!=='GET') return;
  const u=new URL(req.url);
  const isImg=req.destination==='image'||/wikimedia|wikipedia/.test(u.host);
  const isFont=/fonts\.(googleapis|gstatic)\.com/.test(u.host);
  if(u.origin===location.origin){
    e.respondWith(caches.match(req,{ignoreSearch:true}).then(r=>r||fetch(req).then(n=>{const c=n.clone();caches.open(SHELL).then(x=>x.put(req,c));return n;})));
  }else if(isImg||isFont){
    const name=isFont?SHELL:IMG;
    e.respondWith(caches.open(name).then(c=>c.match(req).then(r=>r||fetch(req).then(n=>{ if(n&&(n.ok||n.type==='opaque')) c.put(req,n.clone()); return n;}).catch(()=>r))));
  }
});

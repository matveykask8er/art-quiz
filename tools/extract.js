const fs=require('fs');
const s=fs.readFileSync('index.html','utf8');
const a=s.indexOf('const PAINTINGS = ['), b=s.indexOf('const AUTHOR_PERIOD');
const P=new Function(s.slice(a,b)+';return PAINTINGS')();
fs.writeFileSync('tools/data.json',JSON.stringify(P));
console.log(P.length);

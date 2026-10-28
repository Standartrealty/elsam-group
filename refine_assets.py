import json,re,html
from pathlib import Path
from PIL import Image
R=Path(__file__).parent;S=R/'source-content';c=json.loads((S/'catalog.json').read_text());look={a['url']:R/a['local'] for a in c['assets'] if 'local'in a};data=json.loads((R/'data.json').read_text());plans={p['imageSource'] for p in json.loads((R/'home-plans.json').read_text())}
def save(url,name):
 im=Image.open(look[url]);im.thumbnail((1600,1600));path=R/'assets'/(name+'.webp');im.save(path,'WEBP',quality=84);return '/assets/'+path.name
for p in data:
 source=html.unescape((S/('projects_'+p['id']+'.html')).read_text());urls=list(dict.fromkeys(re.findall(r'https://static.tildacdn.com/[^\s\x22\x27<>\\]+\.(?:jpg|png)',source)));good=[]
 for u in urls:
  if u in plans or u not in look:continue
  try:
   im=Image.open(look[u]);w,h=im.size
   if w>650 and h>400:good.append(u)
  except:pass
 if p['id'] in ['vesna','semiya','rassvet']:p['image']=save(good[0],p['id'])
 p['gallery']=[save(u,p['id']+'-gallery-'+str(i)) for i,u in enumerate(good[:8])]
(R/'data.json').write_text(json.dumps(data,ensure_ascii=False))
# Keep only assets required by the actual public UI; originals remain in the archive.
needed={'hero.webp','selection.webp','hero-film-v1.mp4','logo.svg'}
for p in data:
 for u in [p['image'],*p['gallery']]:needed.add(u.rsplit('/',1)[-1])
for p in json.loads((R/'home-plans.json').read_text()):needed.update([p['image'].rsplit('/',1)[-1],p['thumb'].rsplit('/',1)[-1]])
for p in json.loads((R/'completed.json').read_text()):needed.add(p['image'].rsplit('/',1)[-1])
needed.update(p.name for p in (R/'assets').glob('renovation-*'))
(R/'publish-assets.json').write_text(json.dumps(sorted(needed)))
print('Required assets:',len(needed))

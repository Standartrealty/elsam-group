import json,re,html,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageDraw
from inspect_source import parse
R=Path(__file__).parent;S=R/'source-content';A=R/'assets';A.mkdir(exist_ok=True)
c=json.loads((S/'catalog.json').read_text());lookup={x['url']:R/x['local'] for x in c['assets'] if 'local'in x};usage=[]
def save(url,name=None,width=1400):
 if url not in lookup:return None
 p=lookup[url];name=name or p.stem
 if p.suffix=='.svg':dest=A/(name+'.svg');shutil.copy(p,dest)
 else:
  try:
   im=Image.open(p);im.thumbnail((width,width));dest=A/(name+'.webp');im.save(dest,'WEBP',quality=83)
  except:return None
 usage.append({'source':url,'local':'assets/'+dest.name,'use':name});return '/assets/'+dest.name
def pictures(slug,landscape=True):
 source=html.unescape((S/(slug+'.html')).read_text());urls=list(dict.fromkeys(re.findall(r'https://(?:static|thb).tildacdn.com/[^\s\x22\x27<>\\]+\.(?:jpg|png|webp|jpeg)',source)));result=[]
 for u in urls:
  if u not in lookup:continue
  try:
   im=Image.open(lookup[u]);w,h=im.size
   if w>650 and h>300 and (not landscape or w/h>1.3):result.append(u)
  except:pass
 return result
specs=[('dynasty','Династия','Махачкала','пр. Насрутдинова','IV квартал 2029','до 60 месяцев','от 1 млн ₽'),('vesna','Весна','Каспийск','ул. Байрамова, 14Б','IV квартал 2027','до 36 месяцев','от 1 млн ₽'),('moscow','Москва','Каспийск','ул. Амет-хана Султана, 26/3','IV квартал 2029','уточняется','уточняется'),('semiya','Семья','Махачкала','ул. Байрамова, 7А','ноябрь 2026','уточняется','уточняется'),('rassvet','Рассвет','Махачкала','пр. Насрутдинова, 272И','ноябрь 2026','уточняется','уточняется')]
data=[];allplans=[]
for slug,name,city,address,year,installment,deposit in specs:
 page='projects_'+slug;root=parse(S/(page+'.html'));text=(S/(page+'.txt')).read_text();photos=pictures(page);cover=save(photos[0],slug) if photos else None
 gallery=[save(u,width=1600) for u in photos[:8]]
 desc=text.split('О проекте',1)[-1].split('Генплан',1)[0].split('1\n\nДом строится',1)[0]
 if len(desc)>4000:desc=name+' — жилой проект компании «Эльсам».'
 adv=text.split('Преимущества',1)[-1].split('Типовые планировки',1)[0];adv=adv[adv.find('Локация'):]
 docs=[]
 for n in root.nodes():
  if n.tag=='a' and 'docs.yandex' in n.a.get('href',''):
   u=n.a['href'];title=n.text().strip().replace('Перейти','').strip()
   if u not in [d['url'] for d in docs]:docs.append({'name':title or 'Документ проекта','url':u})
 plans=[];seen=set()
 for n in root.nodes():
  if 'tn-group' not in n.a.get('class',''):continue
  t=' '.join(n.text().split());m=re.search(r'(.+?)\s+от\s+(\d+[.,]\d+)\s*м²',t)
  imgs=[x.a.get('data-original',x.a.get('src','')) for x in n.nodes() if x.tag=='img']
  if m and len(t)<100 and imgs and imgs[0] not in seen:
   url=imgs[0];seen.add(url);label=m.group(1);area=m.group(2).replace('.',',');im=save(url,width=1600);thumb=save(url,hashlib.sha256(url.encode()).hexdigest()[:14]+'-thumb',520)
   if not im:continue
   kind=re.search(r'(\d)-к',label);kind=kind.group(1) if kind else 'all'
   label=label.replace('-к','-комнатная');p={'id':slug+'-'+str(len(plans)+1),'projectId':slug,'project':name,'city':city,'type':kind,'name':label,'area':area,'image':im,'thumb':thumb,'source':'https://elsamgroup.ru/projects/'+slug,'imageSource':url};plans.append(p);allplans.append(p)
 data.append({'id':slug,'name':name,'city':city,'address':address,'year':year,'installment':installment,'deposit':deposit,'image':cover,'gallery':gallery,'description':desc.strip(),'advantages':adv.strip(),'plans':plans,'documents':docs,'source':'https://elsamgroup.ru/projects/'+slug,'status':'Скоро старт продаж' if slug=='moscow' else 'Строится'})
(R/'data.json').write_text(json.dumps(data,ensure_ascii=False));(R/'home-plans.json').write_text(json.dumps(allplans,ensure_ascii=False))
completed=[]
for slug,name,address in [('iceberg','Отель «Айсберг»','Каспийск, Халилова, 9Б'),('mall','Торговый центр','Каспийск, Ленина, 16')]:
 photos=pictures('projects_'+slug,False);completed.append({'id':slug,'name':name,'city':address,'year':'','image':save(photos[0],'completed-'+slug) if photos else None,'source':'https://elsamgroup.ru/projects/'+slug})
(R/'completed.json').write_text(json.dumps(completed,ensure_ascii=False))
save(pictures('projects_dynasty')[0],'hero',2000);save(pictures('projects_dynasty')[1],'selection')
for slug in ['renovation','commercial']:
 ps=pictures(slug,False)
 for i,u in enumerate(ps[:4]):save(u,slug+'-'+str(i))
logo=next(x['url'] for x in c['assets'] if x['url'].endswith('/logo.svg'));save(logo,'logo')
(S/'usage-manifest.json').write_text(json.dumps(usage,ensure_ascii=False,indent=2))
print('Projects',len(data),'Plans',len(allplans),'Used assets',len(usage),'completed',[(p['name'],p['image']) for p in completed])

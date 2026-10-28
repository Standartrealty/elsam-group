# -*- coding: utf-8 -*-
import json,re,unicodedata
from pathlib import Path
from html.parser import HTMLParser
R=Path(__file__).parent
class Text(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.skip=0;self.out=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t in ('p','div','h1','h2','h3','li','br') and not self.skip:self.out.append('\n')
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
  if t in ('p','div','h1','h2','h3','li') and not self.skip:self.out.append('\n')
 def handle_data(self,d):
  if not self.skip:self.out.append(d)
for f in (R/'source-content').glob('*.html'):
 p=Text();p.feed(f.read_text());s='\n\n'.join(' '.join(x.split()) for x in ''.join(p.out).splitlines() if x.strip());f.with_suffix('.txt').write_text(s)
a=json.loads((R/'data.json').read_text())
for x in a:
 x['description']=x['description'].split('\n\nТиповые планировки')[0].split('\n\n5 минут')[0]
 if x['id']=='rassvet':x['description']='Жилой комплекс «Рассвет» — масштабный многоквартирный проект компании «Эльсам» с собственной внутренней инфраструктурой.'
 if x['id']=='moscow':x['installment']='до 60 месяцев'
 if x['id'] in ('semiya','rassvet'):x['advantages']='Кладовые помещения для хранения сезонных вещей и инвентаря.\n\nКоммерческие помещения на первых этажах под магазины и сервисы для жителей комплекса и района.'
 else:x['advantages']='\n\n'.join(dict.fromkeys(x['advantages'].split('\n\n')))
 x['description']=unicodedata.normalize('NFC',x['description'])
(R/'data.json').write_text(json.dumps(a,ensure_ascii=False))
l=json.loads((R/'library.json').read_text());l['about']['text']='Компания «Эльсам» создаёт жилые пространства, в которых комфорт, надёжность и продуманная инфраструктура становятся частью повседневной жизни. Мы реализуем современные многоквартирные комплексы в Дагестане, сочетая строгие строительные стандарты с вниманием к реальным потребностям жителей.\n\n17 лет на рынке. 9 объектов введены в эксплуатацию. 100 000 м² сданных площадей. Рассрочка до 5 лет.\n\nСоздаём жильё, которое радует каждый день. Мы видим потенциал там, где другие видят просто территорию.\n\nЗавершённые объекты: отель «Айсберг» — Каспийск, Халилова, 9Б; торговый центр — Каспийск, Ленина, 16.'
(R/'library.json').write_text(json.dumps(l,ensure_ascii=False))

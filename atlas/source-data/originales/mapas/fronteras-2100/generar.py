import sys,json,copy
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'potencias-centrales'/'.libs'))
from shapely.geometry import shape,mapping,Point
from shapely.ops import unary_union
from casos import CASES,LEVELS,SOURCES,AS_OF
def load(n):return json.loads((P/'datos'/n).read_text(encoding='utf-8'))['features']
countries=load('ne_50m_admin_0_countries.geojson')
admins=load('ne_10m_admin_1_states_provinces.geojson')
disputes=load('ne_10m_admin_0_disputed_areas.geojson')
EU=['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia','Finland','France','Germany','Greece','Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia','Spain','Sweden']
features=[]
for i,c in enumerate(CASES,1):
 q=c['geo'];selected=[]
 if q.get('point'):g=Point(c['lon'],c['lat'])
 else:
  if 'country' in q or 'countries' in q or q.get('eu'):
   names=q.get('countries',[q.get('country')]) if not q.get('eu') else EU
   aliases={}
   selected=[f for f in countries if f['properties']['ADMIN'] in [aliases.get(n,n) for n in names]]
   found={f['properties']['ADMIN'] for f in selected}
   missing=[n for n in names if aliases.get(n,n) not in found]
   if missing:raise ValueError((c['id'],missing))
  elif 'admin1Code' in q:selected=[f for f in admins if f['properties'].get('iso_3166_2')==q['admin1Code'] or (q['admin1Code']=='ES-CT' and f['properties'].get('iso_3166_2') in ['ES-B','ES-GI','ES-L','ES-T'])]
  elif 'geonunit' in q:selected=[f for f in admins if f['properties'].get('geonunit')==q['geonunit']]
  elif 'disputed' in q:selected=[f for f in disputes if f['properties'].get('BRK_NAME')==q['disputed']]
  elif q.get('srpska'):selected=[f for f in admins if f['properties'].get('geonunit')=='Republic Srpska' and f['properties'].get('iso_3166_2')!='BA-BRC']
  elif q.get('vojvodina'):selected=[f for f in disputes if f['properties'].get('NAME')=='Vojvodina']
  elif q.get('westPapua'):selected=[f for f in admins if f['properties'].get('admin')=='Indonesia' and ('Papua' in (f['properties'].get('name') or '') or 'Papua' in (f['properties'].get('name_en') or ''))]
  if not selected:raise ValueError(('No geometry',c['id'],q))
  g=unary_union([shape(f['geometry']).buffer(0) for f in selected]).simplify(.012,preserve_topology=True)
  assert g.is_valid and not g.is_empty,c['id']
 p={k:v for k,v in c.items() if k not in ['geo','sourceKeys']}
 p.update(number=i,color=LEVELS[c['level']]['color'],levelLabel=LEVELS[c['level']]['label'],sources=[dict(title=SOURCES[k][0],url=SOURCES[k][1]) for k in c['sourceKeys']],approx=True)
 features.append(dict(type='Feature',properties=p,geometry=mapping(g)))
base=[]
for f in countries:
 g=shape(f['geometry']).simplify(.06,preserve_topology=True)
 base.append(dict(type='Feature',properties=dict(name=f['properties']['ADMIN']),geometry=mapping(g)))
data=dict(asOf=AS_OF,horizon=2101,levels=LEVELS,base=dict(type='FeatureCollection',features=base),cases=dict(type='FeatureCollection',features=features))
(P/'mapa-datos.js').write_text('window.FUTURE_MAP='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
(P/'fronteras-2101.geojson').write_text(json.dumps(data['cases'],ensure_ascii=False),encoding='utf-8')
limits='Prospectiva cualitativa a 2101, revisada el 06-11-2026. Las áreas localizan casos: no delimitan futuras fronteras ni equivalen a reconocimiento internacional. Natural Earth usa convenciones de facto y contiene contornos desactualizados; véase cada ficha. Los horizontes no son fechas de sucesos.'
frames=[]
for year in [2026,2035,2050,2101]:
 fs=[]
 for f in features:
  p=f['properties'];fs.append(dict(type='Feature',geometry=f['geometry'],properties=dict(id=p['id'],name=p['name'],color=p['color'],role='influence' if p['kind']=='Integración' else 'claim',note=p['current']+' '+('Horizonte: '+p['outlook']+' Condiciones: '+p['conditions'] if year!=2026 else 'Consulte los horizontes posteriores para la hipótesis.'),certainty='documented' if year==2026 else 'scenario',approx=True,sourceUrls=[s['url'] for s in p['sources']],forecastLevel=p['level'],forecastType=p['kind'])))
 frames.append(dict(year=year,title='Situación de referencia' if year==2026 else 'Horizonte de revisión '+str(year),text='Mismos territorios de referencia; las fichas distinguen situación y posibilidades. No se simula una fecha de independencia, anexión o adhesión.',historical=year==2026,features=fs))
scenario=dict(id='fronteras-2101',title='Fronteras hacia el siglo XXII',subtitle='38 casos · procesos, posibilidades y continuidad',era='Prospectiva',region='Mundo',divergence=2026,color='#398d7c',center=[20,15],zoom=2,world=True,tags=['Futuro','Geopolítica','2101'],summary='Atlas de casos territoriales hasta el inicio del siglo XXII: Bougainville, Transnistria, Osetia del Sur y otros 35. Las categorías son juicios editoriales, sin porcentajes estadísticos.',limits=limits,sources=[dict(title=t,url=u) for t,u in SOURCES.values()],frames=frames,ports=[],routes=[])
(P/'escenario.json').write_text(json.dumps(scenario,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
report=['# Fronteras hacia el siglo XXII','',limits,'','No es posible enumerar de antemano todos los cambios reales. Selección de 38 casos a partir de los chats recuperados y revisión de fuentes. No se asignan probabilidades numéricas. Proceso formal encaminado describe la existencia de un proceso, no garantiza su resultado. Integración, reconocimiento, autonomía, república e independencia son fenómenos diferentes.','', '## Casos','']
for f in features:
 p=f['properties'];report += [f"### {p['number']}. {p['name']} — {p['levelLabel']}",'',p['current'],'',p['outlook'],'','Condiciones: '+p['conditions'],'',*[f"- [{s['title']}]({s['url']})" for s in p['sources']],'']
report+=['## Cartografía y reproducción','','Natural Earth, dominio público. Contornos generalizados para localizar casos; no cartografía jurídica ni frentes militares actuales. Srpska excluye Brčko; Karabaj utiliza un contorno histórico como localizador. Sandžak y noreste sirio son puntos para evitar inventar límites. El área de la UE es una referencia de miembros actuales, no una federación proyectada.','', 'Abrir mapa.html junto a mapa-datos.js. Para regenerar: ejecutar generar.py con Shapely disponible. Datos abiertos: fronteras-2101.geojson; integración en el atlas: escenario.json.']
(P/'LEEME.md').write_text('\n'.join(report),encoding='utf-8')
print('Generados',len(features),'casos; áreas',sum(f['geometry']['type']!='Point' for f in features))

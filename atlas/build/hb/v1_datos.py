"""Adaptadores reproducibles para un atlas temporal. Fechas discretas, nunca interpolación de fronteras."""
# Port of atlas-escenarios/scripts/build_data.py (sha256 6b6478f2…, frozen in source-data/originales).
# Changes: inputs from frozen originals and verified HB layers (comun.py), geometry() honours
# ATLAS_TOLERANCE, nothing is written: export() returns the scenarios and LAND.
import sys,json,re,copy,hashlib,unicodedata
from pathlib import Path
import comun
from shapely.geometry import shape,mapping,box
from shapely.ops import unary_union
from shapely import make_valid
def read(p):
 # HB layers come from the verified bases; everything else from the frozen originals.
 n=Path(p).name
 return json.loads((comun.hb_path(n) if n.startswith('world_') else comun.orig_path(p)).read_text(encoding='utf-8'))
def geometry(g):return comun.out_geometry(g)
def feature(name,g,color,role='sovereign',note='',certainty='scenario',approx=True,**extra):
 return dict(type='Feature',geometry=geometry(g),properties=dict(name=name,color=color,role=role,note=note,certainty=certainty,approx=approx,**extra))
def normalize(fc):
 result=[]
 for f in fc['features']:
  p=f['properties'];n=p.get('name','Territorio');c=p.get('color','#d9d4c5');cat=p.get('category',p.get('kind',p.get('cat','')))
  role='sovereign'
  if c.startswith('url'):role='claim';c='#ac8972'
  if p.get('project'):role='claim'
  elif cat in ['occupation','east'] or 'ocupaci' in cat.lower() or 'administraci' in cat.lower():role='occupation'
  elif cat in ['client','italian'] or 'restringida' in cat:role='dependent'
  elif cat=='imperial':role='influence'
  result.append(feature(n,shape(f['geometry']),c,role,p.get('note',''),approx=p.get('approx',True)))
 return result
def frame(year,title,text,features,historical=False):
 # Cada etapa posee sus metadatos: no compartir objetos mutables entre años.
 features=copy.deepcopy(features)
 for f in features:
  p=f['properties'];p['historicalBasis']=p.get('certainty')=='documented'
  p['certainty']='documented' if historical else 'scenario'
 return dict(year=year,title=title,text=text,features=features,historical=historical)
def source(title,url):return dict(title=title,url=url)
base38=read('mapas/victoria-eje/datos/world_1938.geojson');base94=read('mapas/victoria-eje/datos/world_1994.geojson');base14=read('mapas/potencias-centrales/datos/world_1914.geojson');base16=read('mapas/monarquia-universal/datos/world_1600.geojson')
land=unary_union([make_valid(shape(f['geometry'])).buffer(0) for f in base94['features'] if f.get('geometry')]);land=land.intersection(box(-180,-60,180,83)).simplify(.045,preserve_topology=True)
LAND=mapping(land)
def base_features(fc,extent,colors):
 out=[]
 spanish={'German Empire':'Imperio alemán','Germany':'Alemania','Austro-Hungarian Empire':'Austria-Hungría','Ottoman Empire':'Imperio otomano','Russian Empire':'Imperio ruso','USSR':'Unión Soviética','France':'Francia','Kingdom of Italy':'Italia','Italy':'Italia','United Kingdom of Great Britain and Ireland':'Reino Unido e Irlanda','United Kingdom':'Reino Unido','Spain':'España','Portugal':'Portugal','Belgium':'Bélgica','Netherlands':'Países Bajos','Luxembourg':'Luxemburgo','Denmark':'Dinamarca','Norway':'Noruega','Sweden':'Suecia','Finland':'Finlandia','Switzerland':'Suiza','Greece':'Grecia','Serbia':'Serbia','Montenegro':'Montenegro','Albania':'Albania','Romania':'Rumanía','Bulgaria':'Bulgaria','Hungary':'Hungría','Czechoslovakia':'Checoslovaquia','Yugoslavia':'Yugoslavia','Poland':'Polonia','Estonia':'Estonia','Latvia':'Letonia','Lithuania':'Lituania','Turkey':'Turquía','Ireland':'Irlanda','Austria':'Austria','Armenia':'Armenia'}
 for f in fc['features']:
  if not f.get('geometry'):continue
  g=make_valid(shape(f['geometry'])).buffer(0).intersection(extent)
  n=f['properties'].get('NAME')
  if n and not g.is_empty:out.append(feature(spanish.get(n,n),g,colors.get(n,'#cfc7b8'),note='Capa histórica de referencia, generalizada a escala continental. Sus límites no equivalen a una reconstrucción local exacta.',certainty='documented',approx=True))
 return out
SC=[]
# 1. Herencia de Carlos: conservar las geometrías existentes, añadir hitos y disponibilidad temporal.
mon=normalize(read('mapas/monarquia-universal/datos/escenario.geojson'))
imperial_space=unary_union([make_valid(shape(f['geometry'])).buffer(0) for f in base16['features'] if f['properties'].get('NAME')=='Holy Roman Empire']).difference(unary_union([shape(f['geometry']) for f in mon]))
mon.insert(0,feature('Sacro Imperio · estados con gobierno propio',imperial_space,'#d8ccaa','influence','Relación institucional con un emperador electivo. Estos estados conservan sus gobiernos y no son posesiones directas de la monarquía común.',certainty='documented'))
def mono_filter(mode):
 out=[]
 for f in mon:
  n=f['properties']['name'];keep=True
  if mode==1556 and any(t in n for t in ['Portugal','portugu','Brasil','Filipinas','Río de la Plata']):keep=False
  if keep:out.append(f)
 return out
ports=read('mapas/monarquia-universal/datos/puertos_y_rutas.json')
SC.append(dict(id='carlos',title='La herencia de Carlos',subtitle='Una monarquía entre cuatro continentes',era='Edad Moderna',region='Europa · Mundo',divergence=1556,color='#955067',center=[45,9],zoom=4,world=True,tags=['Unión Ibérica','Dinastías'],summary='Las ramas hispánica y austríaca acuerdan una sucesión común. Portugal se integra en 1580 y los Países Bajos permanecen unidos por un pacto político.',limits='Subdivisiones centroeuropeas y superficies coloniales aproximadas. El Sacro Imperio conserva sus gobiernos propios; el vínculo imperial no equivale a soberanía directa.',sources=[source('Abdicación de Carlos (1555–1556)','https://germanhistorydocs.org/en/from-the-reformations-to-the-thirty-years-war-1500-1648/the-abdication-of-emperor-charles-v-1555-56'),source('Dignidad imperial electiva','https://www.habsburger.net/en/glossary/holy-roman-empire'),source('Red portuguesa de enclaves','https://asia.si.edu/whats-on/exhibitions/encompassing-the-globe-portugal-and-the-world-in-the-16th-and-17th-centuries/'),source('Galeón de Manila','https://www.metmuseum.org/es/essays/the-manila-galleon-trade-1565-1815')],frames=[frame(1556,'Un pacto sucesorio común','Divergencia: Fernando y Felipe pactan mantener las coronas bajo una estructura dinástica común. La geografía de 1600 aproxima esta primera etapa.',mono_filter(1556)),frame(1580,'Portugal entra en la Monarquía','La unión ibérica histórica se suma al pacto hispano-austríaco. Se mantiene una administración portuguesa diferenciada.',mono_filter(1580)),frame(1600,'Una red de alcance mundial','Se incorporan las conexiones filipinas y atlánticas. Los enclaves no convierten sus hinterlands en dominios europeos.',mon),frame(1640,'La unión supera la crisis','Hipótesis: un nuevo acuerdo de representación evita la ruptura portuguesa. Conservación política, sin expansión territorial automática.',mon)],ports=[dict(p,start=1565 if p['name'] in ['Manila','Cebú','Acapulco'] else 1580 if p['cat'] in ['port','trade','concession'] else 1556) for p in ports['ports']],routes=[dict(r,start=1565 if 'Manila' in r['name'] else 1580 if r['cat']=='port' else 1556) for r in ports['routes']]))
# 2. Primera Guerra Mundial.
central=normalize(read('mapas/potencias-centrales/datos/escenario.geojson'))
start14=base_features(base14,box(-13,29,60,72),{'German Empire':'#72828b','Austro-Hungarian Empire':'#bf9c56','Ottoman Empire':'#b77f69','Bulgaria':'#7d9c76','France':'#9fb7cb'})
east18=[f for f in central if f['properties']['name'] in ['Finlandia','Ducado Báltico','Lituania','Polonia','Ucrania']]
SC.append(dict(id='centrales',title='Victoria de las Potencias Centrales',subtitle='Una paz bajo hegemonía alemana',era='Siglo XX',region='Europa',divergence=1918,color='#668a97',center=[49,17],zoom=4,tags=['Primera Guerra Mundial','Mitteleuropa'],summary='Una crisis aliada en 1918 conduce a una paz favorable a Alemania y sus socios. Las monarquías centrales sobreviven y el este se reorganiza.',limits='No existió un reparto final acordado por los vencedores. El mapa oriental usa geometrías orientativas; las ocupaciones y la influencia económica no se equiparan a anexiones.',sources=[source('Septemberprogramm','https://www.dhm.de/lemo/kapitel/erster-weltkrieg/innenpolitik/septemberprogramm'),source('Paz de Brest-Litovsk','https://avalon.law.yale.edu/20th_century/bl34.asp'),source('Objetivos búlgaros de guerra','https://history.state.gov/historicaldocuments/frus1917Supp02v01/d404')],frames=[frame(1914,'Europa antes del desenlace','Fronteras de referencia de 1914. Las Potencias Centrales todavía no han obtenido la victoria que supone el escenario.',start14,True),frame(1918,'El nuevo espacio oriental','Etapa interpretativa inspirada en Brest-Litovsk y los proyectos de 1918. La independencia formal admite distintos grados de dependencia.',start14+east18),frame(1920,'Una paz favorable','Escenario completo: Luxemburgo incorporado, Bélgica subordinada y una red de estados orientales vinculados a Alemania.',central),frame(1925,'Consolidación y tensiones','Se mantienen las fronteras supuestas de 1920; la estabilidad interna y las resistencias continúan abiertas.',central)],ports=[],routes=[]))
# 3. Eje: separar ocupaciones de proyectos no realizados.
axis=normalize(read('mapas/victoria-eje/datos/escenario.geojson'));pre38=base_features(base38,box(-13,29,61,72),{'Germany':'#697d86','Italy':'#829b73','USSR':'#bb9c86','France':'#a5b8c6'})
without_projects=[f for f in axis if f['properties']['role']!='claim']
SC.append(dict(id='eje',title='Victoria del Eje en Europa',subtitle='Un continente bajo ocupación',era='Siglo XX',region='Europa · Cáucaso',divergence=1942,color='#8b786e',center=[49,20],zoom=4,tags=['Segunda Guerra Mundial','Ocupación'],summary='Una derrota soviética occidental, la supervivencia de Italia fascista y una paz británica negociada impiden la liberación aliada del continente.',limits='Moscovia, el Cáucaso y otras ampliaciones son proyectos hipotéticos. El dominio nazi implicaba políticas genocidas, explotación y desplazamientos masivos; el color expresa control, no legitimidad.',sources=[source('Administración alemana de Europa en 1942','https://encyclopedia.ushmm.org/content/en/map/german-administration-of-europe-1942'),source('Organización del este: decreto de 1941','https://avalon.law.yale.edu/imt/1997-ps.asp'),source('Generalplan Ost','https://www.dhm.de/lemo/kapitel/der-zweite-weltkrieg/voelkermord/generalplan-ost')],frames=[frame(1938,'La referencia anterior a la guerra','Base de 1938: incluye las alteraciones territoriales recogidas en esa capa; no representa el máximo dominio alemán.',pre38,True),frame(1942,'La ocupación se prolonga','Primera etapa alternativa: se proyecta la continuidad del orden de ocupación. No es una reproducción exacta del frente de un día de 1942.',without_projects),frame(1944,'Expansión del proyecto oriental','Hipótesis: el colapso soviético occidental permite ampliar las administraciones coloniales. Los límites se dibujan como propuestas.',axis),frame(1948,'El orden europeo del escenario','Paz negociada con Londres y supervivencia italiana. Las fronteras proyectadas siguen siendo interpretativas.',axis)],ports=[],routes=[]))
# 4. Gran Alemania: recuperar los datos GIS originales del mapa que ya tenía el usuario.
# extract_original.py, in memory: the <script id=geo|data> blocks of the frozen europa_1848.html.
_ga=comun.orig_path('mapas/gran-alemania/europa_1848.html').read_text(encoding='utf-8')
orig,meta=[json.loads(re.search('<script[^>]+id=["\x27]'+i+'["\x27][^>]*>(.*?)</script>',_ga,re.S).group(1)) for i in ['geo','data']]
lookup={str(f['id']):f for f in meta['features']};german=[]
for f in orig['features']:
 p=f['properties'];m=lookup.get(str(p.get('id')),p);cat=m.get('cat',p.get('cat','context'));n=m.get('name',p.get('name','Territorio'))
 if cat=='context':continue
 color=meta['categories'].get(cat,['','#d8cdb4'])[1];role='claim' if cat in ['diaspora','dynasty','conflict','uncertain'] else 'sovereign'
 german.append(feature(n,shape(f['geometry']),color,role,' '.join(str(m.get(k,'')) for k in ['bund','viabilidad','obstaculos','nota']),approx=cat not in ['core','east','exception'],originalCategory=cat,sourceUrls=[meta['sources'][i][1] for i in m.get('fuentes',[]) if 0<=i<len(meta['sources'])]))
core=[f for f in german if f['properties']['originalCategory'] in ['core','exception']];expanded=[f for f in german if f['properties']['originalCategory'] in ['core','exception','east']]
SC.append(dict(id='gran-alemania',title='La solución granalemana',subtitle='Fráncfort encuentra un acuerdo',era='Siglo XIX',region='Europa central',divergence=1849,color='#98506a',center=[49,13],zoom=5,tags=['1848','Unificación alemana'],summary='Los estados alemanes y las tierras austríacas confederales acuerdan una unificación constitucional. Las posesiones no confederales conservan un estatuto diferenciado.',limits='Se recupera el GIS del atlas original. Los tonos claros son vínculos o reclamaciones, no anexiones automáticas de Hungría. Großdeutschland y Großösterreich siguen siendo proyectos distintos.',sources=[source('GIS histórico de la Confederación en 1848','https://geo.nyu.edu/catalog/harvard-ghgis1848germanconfed'),source('Fuente original conservada','https://github.com/aourednik/historical-basemaps')],frames=[frame(1848,'La base confederal','Territorios de la Confederación anteriores a las admisiones prusianas de abril. No constituyen todavía un Estado unificado.',core,True),frame(1849,'Acuerdo constitucional','Divergencia: se supera el bloqueo sucesorio y austríaco. Se representa el núcleo de la nueva unión.',expanded),frame(1851,'Vínculos con la monarquía habsbúrgica','Variante ampliada: se muestran por separado las relaciones dinásticas y las incorporaciones discutidas.',german)],ports=[],routes=[]))
def getgeom(fc,*names):return unary_union([make_valid(shape(f['geometry'])).buffer(0) for f in fc['features'] if f.get('geometry') and f['properties'].get('NAME') in names])
# 5. Nuevo: victoria japonesa. Separar territorio imperial, gobiernos dependientes y conquistas.
japan38=getgeom(base38,'Empire of Japan');manchu=japan38.intersection(getgeom(base94,'China')).intersection(box(115,38,135,54));imperial=japan38.difference(manchu)
jbase=[feature('Imperio japonés · territorio imperial',imperial,'#b46d73',note='Japón, Corea, Taiwán y otras posesiones imperiales de la capa de 1938; Corea y Taiwán no eran estados aliados.',certainty='documented'),feature('Manchukuo',manchu,'#d8a4a0','dependent','Estado dependiente de Japón, diferenciado del territorio imperial. Delimitación aproximada.',certainty='documented')]
china=getgeom(base38,'Chinese warlords');nanjing=china.intersection(box(115,23,123,35))
chinese=feature('Gobierno de Nankín · zona dependiente',nanjing,'#d7aa87','dependent','Escenario inspirado en el gobierno de Wang Jingwei. El contorno costero es esquemático; no reproduce su control efectivo en una fecha exacta.')
south=[feature('Tailandia · aliada de Japón',getgeom(base38,'Siam'),'#94a77c',note='Aliada con gobierno propio; no territorio imperial japonés.'),feature('Filipinas · Estado dependiente',getgeom(base38,'Philippines'),'#d8b284','dependent','Se prolonga el régimen dependiente establecido en 1943, bajo predominio militar y económico japonés.'),feature('Birmania · Estado dependiente',getgeom(base94,'Myanmar','Burma'),'#d8b284','dependent','Estado de Ba Maw prolongado hipotéticamente. Se usa una frontera posterior como guía, sin añadir las cesiones locales a Tailandia.'),feature('Indochina · tutela japonesa',getgeom(base38,'French Indo-China','Laos','Cambodia'),'#c9af93','occupation','La administración colonial y la presencia japonesa evolucionaron durante la guerra. Aquí se supone una tutela japonesa consolidada tras la victoria.'),feature('Malaya y Borneo británico · ocupación',getgeom(base38,'Malaysia'),'#a8bec0','occupation','Las antiguas colonias británicas se conservan en el perímetro japonés. No se presenta un reparto final ya pactado.'),feature('Indias Orientales Neerlandesas · control japonés',getgeom(base38,'Dutch East Indies'),'#a8bec0','occupation','Se prolonga el control japonés sobre el archipiélago. Esta geometría generaliza una ocupación con fuertes diferencias locales.')]
independent=[copy.deepcopy(f) for f in south]
for f in independent:
 if 'Neerlandesas' in f['properties']['name']:f['properties'].update(name='Indonesia · independencia tutelada',color='#d8b284',role='dependent',note='Variante hipotética de aplicación de la promesa de independencia de 1944. No supone una independencia efectiva libre de presión japonesa.')
china_influence=feature('China · hegemonía japonesa disputada',china.difference(nanjing),'#c5bca1','influence','La victoria fuerza concesiones y predominio japonés; el interior no se considera ocupado de forma homogénea. Persisten poderes y resistencias chinas.')
SC.append(dict(id='japon',title='Victoria japonesa en Asia-Pacífico',subtitle='Un imperio y su esfera de predominio',era='Siglo XX',region='Asia · Pacífico',divergence=1942,color='#b46d73',center=[24,117],zoom=3.5,world=True,tags=['Japón','Estados dependientes'],summary='Un desenlace militar favorable permite a Japón conservar sus conquistas y organizar una esfera asiática de estados dependientes, aliados y administraciones militares.',limits='No hay conquista de Estados Unidos ni de Australia. Las categorías no equiparan independencia formal y soberanía real. China e Indochina están generalizadas; los límites son aproximados.',sources=[source('Política japonesa de Gran Asia Oriental, 1943','https://www.jacar.go.jp/english/exhibition/showa100/01_03.html'),source('Declaración de 1943: archivo japonés','https://www.jacar.archives.go.jp/das/meta-en/C14020058100'),source('Evaluación estratégica aliada de 1943','https://history.state.gov/historicaldocuments/frus1943CairoTehran/d231')],frames=[frame(1938,'El imperio y Manchukuo','Referencia de 1938. Se separan las posesiones imperiales de Manchukuo; el frente sinojaponés no se reconstruye en detalle.',jbase,True),frame(1940,'La China dependiente','Representación aproximada de un poder dependiente en Nankín. Su independencia nominal no implica control de toda China.',jbase+[chinese]),frame(1943,'El perímetro meridional se mantiene','Divergencia militar desde 1942: Japón sostiene sus conquistas y su predominio regional. Se distinguen gobiernos y ocupaciones.',jbase+[chinese]+south),frame(1948,'Victoria y descolonización tutelada','Hipótesis: una paz favorable consolida la esfera y se aplica la promesa de independencia indonesia, bajo tutela japonesa.',jbase+[chinese,china_influence]+independent)],ports=[dict(name=n,lat=y,lon=x,cat='hisp',note=t,start=1943) for n,x,y,t in [('Tokio',139.7,35.7,'Centro del poder imperial japonés.'),('Nankín',118.8,32.1,'Sede de un gobierno chino dependiente.'),('Singapur',103.8,1.3,'Posición naval y comercial estratégica bajo ocupación.'),('Manila',121,14.6,'Centro del régimen filipino dependiente.'),('Batavia',106.8,-6.2,'Centro administrativo colonial y de la ocupación.')]],routes=[dict(name='Corredor de recursos del sur',coordinates=[[139,35],[126,24],[120,15],[104,1],[107,-6]],cat='port',start=1943)]))
# 6. Nuevo: la Gran Colombia consigue sobrevivir a su disolución.
def gran_feature(n,label,color):return feature(label,getgeom(base94,n),color,note='Unidad territorial orientativa basada en la geografía de 1994; no reproduce las fronteras departamentales ni todas las reclamaciones de la Gran Colombia. La pertenencia federal posterior a 1830 es hipotética.')
gcol=gran_feature('Colombia','Nueva Granada · componente federal','#8c9c74');gven=gran_feature('Venezuela','Venezuela · componente federal','#bf9c5f');gecu=gran_feature('Ecuador','Quito · componente federal','#6e9695');gpan=gran_feature('Panama','Istmo de Panamá · componente federal','#b38373')
gfull=[gcol,gven,gecu,gpan]
g30=[]
for f in gfull:
 f=copy.deepcopy(f);f['properties']['role']='federal';f['properties']['note']+=' Desde 1830 se representa el vínculo federal pactado.';g30.append(f)
SC.append(dict(id='gran-colombia',title='La Gran Colombia federal',subtitle='La unión sobrevive a 1830',era='Siglo XIX',region='América del Sur · Caribe',divergence=1830,color='#879b72',center=[3,-70],zoom=4.25,world=True,tags=['Bolívar','Federación'],summary='Una convención logra conciliar a Venezuela, Nueva Granada y Quito. El istmo permanece en la unión y la república adopta una organización federal duradera.',limits='Las unidades están aproximadas con geometrías posteriores. No representan el mapa jurídico de 1824 ni una ocupación efectiva del interior. Panamá no era entonces un Estado moderno independiente.',sources=[source('El proyecto grancolombiano · Banco de la República','https://enciclopedia.banrepcultural.org/index.php?title=El_proyecto_grancolombiano'),source('Registro histórico de la disolución · Biblioteca del Banco de la República','https://babel.banrepcultural.org/digital/collection/p17054coll26/id/5985/'),source('Separación venezolana y convención de 1830','https://www.mincultura.gob.ve/eventos/venezuela-se-separa-definitivamente-de-la-gran-colombia/')],frames=[frame(1819,'El proyecto republicano','Nueva Granada y Venezuela se representan como componentes del proyecto, no como territorios enteramente pacificados. Contornos orientativos.',[gcol,gven]),frame(1822,'La unión alcanza Quito y el istmo','La incorporación de Quito y Panamá amplía el espacio republicano. No se reconstruyen las campañas ni los doce departamentos de 1824.',gfull),frame(1830,'Un pacto federal evita la ruptura','Divergencia: una convención mantiene la unión con representación y autonomía regional. El mapa cambia de estatuto, no necesita nuevas conquistas.',g30),frame(1850,'Una federación de cuatro componentes','Se mantienen los componentes y se consolidan sus conexiones. No se incorporan automáticamente Perú, Bolivia ni Centroamérica.',g30)],ports=[dict(name=n,lon=x,lat=y,cat='port',start=1830,note='Centro de articulación federal del escenario.') for n,x,y in [('Bogotá',-74.1,4.6),('Caracas',-66.9,10.5),('Quito',-78.5,-.2),('Panamá',-79.5,9),('Cartagena',-75.5,10.4)]],routes=[dict(name='Conexión caribeña de la federación',coordinates=[[-79.5,9],[-75.5,10.4],[-71,12],[-66.9,10.5]],cat='port',start=1830)]))
# 7. Nuevo: Kalmar conserva Suecia por un acuerdo político.
base30=read('world_1530.geojson')
dk=getgeom(base30,'Denmark-Norway');sw=getgeom(base30,'Sweden');dn=feature('Dinamarca y Noruega · coronas vinculadas',dk,'#7897a2',note='Geografía aproximada de 1530. Las coronas y posesiones septentrionales conservan estatutos propios; no se representa un Estado nacional moderno.')
sv=feature('Suecia y Finlandia · corona sueca',sw,'#c4a25e',note='Finlandia forma parte del espacio sueco en este periodo. Se usa la capa de 1530, sin trasladar hacia 1520 las adquisiciones bálticas suecas de finales del siglo XVI.')
kf=[dn,sv];kfed=[]
for f in kf:
 f=copy.deepcopy(f);f['properties'].update(color='#7a9b87',note=f['properties']['note']+' Desde 1536 se supone un consejo común pactado, sin abolir las leyes de cada reino.');kfed.append(f)
SC.append(dict(id='kalmar',title='La Unión de Kalmar perdura',subtitle='Tres coronas, un poder nórdico',era='Edad Moderna',region='Escandinavia · Báltico',divergence=1523,color='#7192a0',center=[61,16],zoom=3.75,world=True,tags=['Escandinavia','Unión de coronas'],summary='Una salida negociada a la crisis sueca mantiene la unión de Dinamarca, Noruega y Suecia. Un consejo compartido reduce la primacía danesa y coordina la política exterior.',limits='Se usan contornos de 1600 para una reconstrucción generalizada. No se inventan conquistas bálticas, dominio sobre Rusia o una colonización americana automática. La unión no estuvo libre de rupturas antes de 1523.',sources=[source('Historia de la Unión de Kalmar · Lex / Aarhus','https://lex.dk/Kalmarunionen'),source('Cronología de la crisis y la ruptura','https://lex.dk/tidslinje_over_Kalmarunionen%2C_1397-1523'),source('La unión y los tres reinos · Store norske leksikon','https://snl.no/Kalmarunionen')],frames=[frame(1520,'Tres reinos en crisis','La unión se enfrenta a una crisis de legitimidad. El mapa usa geografía de 1600 como aproximación, no representa el control efectivo tras el baño de sangre de Estocolmo.',kf),frame(1523,'Un acuerdo evita la separación','Divergencia: los estamentos suecos aceptan una unión renegociada en lugar de la ruptura permanente.',kf),frame(1536,'Consejo común de las coronas','Se supone una coordinación política pactada. El cambio visible de color expresa el nuevo estatuto común, no una anexión danesa.',kfed),frame(1600,'Un bloque nórdico duradero','La unión conserva sus componentes y sus rutas bálticas. Sus rivales y las sociedades locales siguen teniendo intereses propios.',kfed)],ports=[dict(name=n,lon=x,lat=y,cat='port',start=1536,note='Centro político o comercial de una de las coronas de la unión.') for n,x,y in [('Copenhague',12.57,55.68),('Estocolmo',18.07,59.33),('Bergen',5.32,60.39),('Turku',22.27,60.45)]],routes=[dict(name='Conexión de las coronas bálticas',coordinates=[[12.57,55.68],[16,57],[18.07,59.33],[22.27,60.45]],cat='port',start=1536)]))
future_path=comun.orig_path('mapas/fronteras-2100/escenario.json')
if future_path.exists(): SC.append(json.loads(future_path.read_text(encoding='utf-8')))

def curate():
 for s in SC:
  if s['id']=='gran-alemania':s['sources']=[source(t,u) for t,u,_ in meta['sources']]
  if s['id']=='kalmar':
   s['limits']='Contornos de 1530 como aproximación de la unión. No se trasladan a 1520 las adquisiciones bálticas suecas de finales del siglo XVI. El escenario conserva las coronas sin añadir conquistas automáticas.'
   s['frames'][0]['text']='La unión entra en una crisis de legitimidad. La capa de 1530 aproxima la geografía; no se reconstruye el control militar efectivo tras el baño de sangre de Estocolmo.'
  if s['id']=='carlos':
   dates={'Manila':1571,'Cebú':1565,'Acapulco':1565,'Luanda':1576,'Río de Janeiro':1565,'Buenos Aires':1580,'Portobelo':1597}
   for p in s['ports']:
    if p['name'] in dates:p['start']=max(p['start'],dates[p['name']])
  for fr in s['frames']:
   fr['basis']='historical-reference' if fr['historical'] else 'counterfactual-interpretation'
   fr['geometryPolicy']='discrete-snapshot-no-interpolation'
   fr['geographyNote']=s['limits']
   for f in fr['features']:
    p=f['properties']
    # Identidad estable entre etapas; permitir componentes separados de un mismo Estado.
    raw=p['name']+'|'+json.dumps(f['geometry'],sort_keys=True,separators=(',',':'))
    p['id']=s['id']+'-'+hashlib.sha256(raw.encode('utf-8')).hexdigest()[:14]
    p['entityId']=s['id']+'-'+hashlib.sha256(p['name'].encode('utf-8')).hexdigest()[:12]
    p['validAt']=fr['year']
    p.setdefault('sourceUrls',[src['url'] for src in s['sources']])
    if f['geometry']['type'] in ['Point','MultiPoint']:
     p['representation']='location-marker'
     p['approx']=True
    else:p['representation']='area'

def export():
 curate()
 for s in SC:
  for j,fr in enumerate(s['frames']):
   for i,f in enumerate(fr['features']):f['properties'].setdefault('id',s['id']+'-'+str(i))
  # The port writes nothing: build/generar_hb.py and the equivalence test consume SC.
 return SC

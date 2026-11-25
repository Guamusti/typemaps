"""Migrates the maps that already have an original vector source to contract v2 (atlas/CONTRATO.md):
gran-alemania (europa_1848.html), carlos, centrales, eje (mapas/*/datos/escenario.geojson) and
fronteras-2101 (mapas/fronteras-2100). Geometries are copied verbatim (no simplify, no rounding, no
make_valid). Stages that need historical-basemaps layers are left for task 2.5 and listed in pendingYears.
Reads the frozen copies in atlas/source-data/originales/. Usage: python3.12 -I migrar_originales.py"""
import ast, hashlib, json, re
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[1]
ORIG = ATLAS / 'source-data' / 'originales'
OUT = ATLAS / 'data'
SPLIT_BYTES = 2_000_000  # CONTRATO §2: geometries go to <id>.geo.js above ~2 MB
HB_LICENSE = dict(name='GPL-3.0 (historical-basemaps)', url='https://github.com/aourednik/historical-basemaps/blob/master/LICENSE', scope='Base cartográfica de la que derivan las geometrías del escenario')
NE_LICENSE = dict(name='Dominio público (Natural Earth)', url='https://www.naturalearthdata.com/about/terms-of-use/', scope='Áreas de referencia de los casos')

def canon(g):
    return hashlib.sha256(json.dumps(g, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
def read(rel): return (ORIG / rel).read_text(encoding='utf-8')
def load(rel): return json.loads(read(rel))
def sha_file(rel): return hashlib.sha256((ORIG / rel).read_bytes()).hexdigest()

# ---- texts of maps and stages, read from build_data.py with ast (no hand-copied strings) ----
BUILD = read('atlas-escenarios/scripts/build_data.py')
def const(n):
    try: return ast.literal_eval(n)
    except (ValueError, TypeError, SyntaxError): return None
SCEN = {}
for node in ast.walk(ast.parse(BUILD)):
    if isinstance(node, ast.Call) and getattr(node.func, 'attr', '') == 'append' and getattr(node.func.value, 'id', '') == 'SC':
        kw = {k.arg: k.value for k in node.args[0].keywords}
        if const(kw.get('id')) not in ('carlos', 'centrales', 'eje', 'gran-alemania'): continue
        d = {k: const(v) for k, v in kw.items() if const(v) is not None}
        d['frames'] = {}
        for fr in kw['frames'].elts:
            a = fr.args
            d['frames'][a[0].value] = dict(title=a[1].value, text=a[2].value, historical=len(a) > 4 and a[4].value is True)
        d['sources'] = [dict(title=s.args[0].value, url=s.args[1].value) for s in kw['sources'].elts] if isinstance(kw['sources'], ast.List) else []
        SCEN[d['id']] = d

def role_v1(p, color):
    # Exact copy of normalize() in build_data.py: provisional role table until report R2.
    cat = p.get('category', p.get('kind', p.get('cat', '')))
    role = 'sovereign'
    if color.startswith('url'): role = 'claim'
    if p.get('project'): role = 'claim'
    elif cat in ['occupation', 'east'] or 'ocupaci' in cat.lower() or 'administraci' in cat.lower(): role = 'occupation'
    elif cat in ['client', 'italian'] or 'restringida' in cat: role = 'dependent'
    elif cat == 'imperial': role = 'influence'
    return role

def svg_patterns(text, names):
    out = {}
    for n in names:
        m = re.search(r'<pattern id="' + n + r'"([^>]*)>(.*?)</pattern>', text, re.S)
        a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        rot = re.search(r'rotate\(([-\d.]+)\)', a.get('patternTransform', ''))
        out[n] = dict(width=float(a['width']), height=float(a['height']), rotate=float(rot.group(1)) if rot else 0, content=m.group(2))
    return out

def bounds(geoms):
    xs, ys = [], []
    def walk(c):
        if isinstance(c[0], (int, float)): xs.append(c[0]); ys.append(c[1])
        else:
            for x in c: walk(x)
    def geom(g):
        if g['type'] == 'GeometryCollection':
            for x in g['geometries']: geom(x)
        else: walk(g['coordinates'])
    for g in geoms: geom(g)
    return [[round(min(ys), 4), round(min(xs), 4)], [round(max(ys), 4), round(max(xs), 4)]]

class Map:
    def __init__(self, mid, kind, origin_rel):
        self.id, self.kind, self.origin = mid, kind, origin_rel
        self.geometries, self.registry = {}, {}
    def gid(self, g, origin, entity):
        h = canon(g); gid = 'g-' + h[:16]
        if gid in self.geometries: assert canon(self.geometries[gid]) == h, 'gid collision'
        self.geometries[gid] = g
        r = self.registry.setdefault(gid, dict(sha256=h, origin=origin, entityIds=[]))
        if entity not in r['entityIds']: r['entityIds'].append(entity)
        return gid

def frame(year, info, feats, basis=None):
    hist = info['historical']
    out = []
    for e in feats:
        f = dict(id=f"{e['entityId']}@{year}", **e)
        f['certainty'] = e.get('certainty') or ('documented' if hist else 'scenario')
        out.append({k: v for k, v in f.items() if v is not None})
    return dict(year=year, title=info['title'], text=info['text'], historical=hist,
                basis=basis or ('historical-reference' if hist else 'counterfactual-interpretation'), features=out)

def entity(m, idx, origin_rel, g, name, category, color, role, note, attrs, precision, pattern=None, source_urls=None, entity_id=None, historical_basis=False):
    eid = entity_id or f'f{idx:03d}'
    marker = g['type'] in ('Point', 'MultiPoint')
    origin = f'{origin_rel}features[{idx}]' if origin_rel.endswith('.') else f'{origin_rel}#features[{idx}]'
    return dict(entityId=eid, gid=m.gid(g, origin, eid), name=name, category=category,
                color=color, pattern=pattern, role=role, historicalBasis=historical_basis,
                precision='approximate' if marker else precision,
                representation='location-marker' if marker else 'area', note=note or None, attrs=attrs or None,
                sourceUrls=source_urls or None)

MAPS, CATALOG, MANIFEST = [], [], {}

def emit(m, payload, cat):
    payload = dict(schema=2, id=m.id, kind=m.kind, **payload)
    payload['meta'] = dict(origin=m.origin, originSha256=sha_file(m.origin), generator='atlas/build/migrar_originales.py',
                           simplified=False, crs='EPSG:4326', **payload.get('meta', {}))
    geo = json.dumps(m.geometries, ensure_ascii=False, separators=(',', ':'))
    head = '// Generated by atlas/build/migrar_originales.py; do not edit by hand. Contract v2 (atlas/CONTRATO.md).\n'
    if len(geo.encode('utf-8')) > SPLIT_BYTES:
        geo_js = head + 'window.ATLAS_REGISTER_GEO(' + json.dumps(dict(id=m.id, geometries=m.geometries), ensure_ascii=False, separators=(',', ':')) + ');\n'
        (OUT / f'{m.id}.geo.js').write_text(geo_js, encoding='utf-8', newline='\n')
        cat['geoFile'] = f'{m.id}.geo.js'
        cat['geoSha256'] = hashlib.sha256(geo_js.encode('utf-8')).hexdigest()
    else:
        payload['geometries'] = m.geometries
    js = head + 'window.ATLAS_REGISTER(' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ');\n'
    (OUT / f'{m.id}.js').write_text(js, encoding='utf-8', newline='\n')
    cat.update(file=f'{m.id}.js', dataSha256=hashlib.sha256(js.encode('utf-8')).hexdigest())
    CATALOG.append(cat)
    MANIFEST[m.id] = m.registry
    # Open download: one feature per entity and geometry (not per stage, to avoid repeating geometries),
    # with the stages where it appears and the certainty of each stage.
    grouped = {}
    for fr in payload['frames']:
        for f in fr['features']:
            key = (f['entityId'], f['gid'])
            p = grouped.setdefault(key, dict({k: v for k, v in f.items() if k not in ('gid', 'id', 'certainty')}, years=[], certaintyByYear={}))
            p['years'].append(fr['year']); p['certaintyByYear'][str(fr['year'])] = f['certainty']
    fc = dict(type='FeatureCollection', mapId=m.id, kind=m.kind,
              features=[dict(type='Feature', geometry=m.geometries[g], properties=p) for (_, g), p in grouped.items()])
    (OUT / f'{m.id}.geojson').write_text(json.dumps(fc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8', newline='\n')
    print(m.id, {fr['year']: len(fr['features']) for fr in payload['frames']}, len(m.geometries), 'geometrías', len(js) // 1024, 'KB', '+ geo' if 'geoFile' in cat else '')

def catalog_entry(m, s, years, pending, legend, bounds_, views, license_, extra_limits=''):
    return dict(id=m.id, kind=m.kind, title=s['title'], subtitle=s.get('subtitle'), era=s['era'], region=s['region'],
                years=years, pendingYears=pending or None, divergence=s.get('divergence'), bounds=bounds_, views=views,
                tags=s.get('tags', []), summary=s['summary'], limits=s['limits'] + extra_limits, sources=s['sources'],
                license=license_, legend=legend, preview=None)

# ---- stages and maps derived from historical-basemaps (tasks 2.3, 2.5, 2.6) ----
# The ported v1 generators (build/hb) run here without simplification; their only inputs are the frozen
# originals and the hash-verified HB layers of source-data/BASES.csv. Their output is the "original" of
# these geometries: validar.py regenerates it and compares canonical hashes.
import os, sys
os.environ['ATLAS_TOLERANCE'] = 'none'
sys.path.insert(0, str(ATLAS / 'build' / 'hb'))
import comun, v1_datos, v1_extension  # noqa: E402
_datos = v1_datos.export()
V1 = {s['id']: s for s in json.loads(json.dumps(_datos + v1_extension.export(), ensure_ascii=False))}
DATOS_IDS = {s['id'] for s in _datos}
HB_COMMIT = '4b5039e'
HB_NOTE = f'Geometrías calculadas desde historical-basemaps (commit {HB_COMMIT}, source-data/BASES.csv) con el generador del visor anterior, sin su simplificación'
def hb_script(sid): return 'atlas-escenarios/scripts/' + ('build_data.py' if sid in DATOS_IDS else 'build_extension.py')
def hb_origin(sid, path): return f'{hb_script(sid)}:{sid}#{path}'
# Labels and overlay colours of the v1 viewer (atlas-escenarios/dist/app.js), the original presentation of these maps.
V1_ROLES = [('sovereign', 'Gobierno o soberanía'), ('federal', 'Componente de la federación'), ('dependent', 'Dependencia política'),
            ('occupation', 'Ocupación / administración'), ('influence', 'Vínculo o influencia'), ('claim', 'Proyecto / reclamación')]
def v1_port_color(cat): return '#f8fafc' if cat in ('trade', 'concession') else '#2dd4bf' if cat == 'port' else '#f472b6'
def v1_route_color(cat): return '#2dd4bf' if cat == 'port' else '#f472b6'

def v1_entity(m, sid, k, i, f, eid, category):
    p, g = f['properties'], f['geometry']
    marker = g['type'] in ('Point', 'MultiPoint')
    return dict(entityId=eid, gid=m.gid(g, hb_origin(sid, f'frames[{k}].features[{i}]'), eid), name=p['name'], category=category,
                color=p['color'], role=p['role'], historicalBasis=p.get('historicalBasis', False),
                precision='approximate' if marker else 'generalized', representation='location-marker' if marker else 'area',
                note=p.get('note') or None, sourceUrls=p.get('sourceUrls') or None,
                start=p.get('start'), end=p.get('end'), period=p.get('period'), lost=p.get('lost'))

def hb_reference(m, sid, k, key):
    """Entities of the HB reference layer that v1 uses as the first stage of centrales and eje."""
    return [v1_entity(m, sid, k, i, f, f'{key}-{i:02d}', key) for i, f in enumerate(V1[sid]['frames'][k]['features'])
            if f['properties']['note'].startswith('Capa histórica de referencia')]

# ======================= gran-alemania =======================
rel = 'mapas/gran-alemania/europa_1848.html'
html = read(rel)
emb = {i: json.loads(re.search('<script[^>]+id=["\']' + i + '["\'][^>]*>(.*?)</script>', html, re.S).group(1)) for i in ['geo', 'data']}
geo, meta = emb['geo'], emb['data']
lookup = {str(f['id']): f for f in meta['features']}
drawn = {}
for mm in re.finditer(r'<g class="([^"]*)"[^>]*data-id="([^"]+)"', html):
    seg = html[mm.start():html.find('</g>', mm.end())]
    fills = [f for f in re.findall(r'fill="([^"]+)"', seg) if f != 'none']
    drawn[mm.group(2)] = (next((f for f in fills if not f.startswith('url')), None), next((f[5:-1] for f in fills if f.startswith('url(#')), None))
m = Map('gran-alemania', 'counterfactual', rel)
s = SCEN['gran-alemania']; s['sources'] = [dict(title=t, url=u) for t, u, _ in meta['sources']]
ROLE48 = {c: ('claim' if c in ['diaspora', 'dynasty', 'conflict', 'uncertain'] else 'sovereign') for c in meta['categories']}
ents, nodrawn = [], []
for i, f in enumerate(geo['features']):
    pid = str(f['properties'].get('id'))
    mt = lookup.get(pid, f['properties'])
    cat = mt.get('cat', f['properties'].get('cat', 'context'))
    fill, pat = drawn.get(pid, (None, None))
    if fill is None: nodrawn.append(pid); fill = meta['categories'][cat][1]
    attrs = {k: v for k, v in mt.items() if k not in ('id', 'name', 'cat', 'fuentes', 'source_ids')}
    e = entity(m, i, rel, f['geometry'], mt.get('name'), cat, fill, ROLE48[cat],
               ' '.join(str(mt.get(k, '')) for k in ['bund', 'viabilidad', 'obstaculos', 'nota']).strip(), attrs, 'source', pat,
               [meta['sources'][j][1] for j in mt.get('fuentes', []) if 0 <= j < len(meta['sources'])], entity_id=pid, historical_basis=True)
    ents.append(e)
members = {1848: ['core', 'exception'], 1849: ['core', 'exception', 'east'], 1851: [c for c in meta['categories'] if c != 'context']}
frames = [frame(y, s['frames'][y], [e for e in ents if e['category'] in cats + ['context']]) for y, cats in members.items()]
legend = [dict(key=k, label=v[0], color=v[1], categories=[k]) for k, v in meta['categories'].items()]
emit(m, dict(legend=legend, patterns=svg_patterns(html, ['diagonal', 'warn']), style=dict(stroke='#857e76', markerStroke='white'),
             sources=[dict(title=t, url=u, note=n) for t, u, n in meta['sources']], frames=frames, ports=[], routes=[],
             meta=dict(referenceDate=geo['metadata'].get('fecha'), colorFallback=nodrawn or None)),
     catalog_entry(m, s, list(members), None, legend, bounds([f['geometry'] for f in geo['features']]),
                   {'Europa 1848': bounds([f['geometry'] for f in geo['features']]),
                    'Confederación': bounds([f['geometry'] for f, e in zip(geo['features'], ents) if e['category'] != 'context'])},
                   [dict(name='Por verificar (tarea 2.9)', url='https://histogis.acdh.oeaw.ac.at/', scope='Geometrías HistoGIS / HGIS Germany del original')],
                   ' Se muestran también las 24 entidades de contexto del original, que el visor anterior descartaba.'))

# ======================= carlos =======================
rel = 'mapas/monarquia-universal/datos/escenario.geojson'
gen = read('mapas/monarquia-universal/generar.py')
COL = ast.literal_eval(re.search(r'^COL=(\{.*?\})$', gen, re.M).group(1))
leg_eu = ast.literal_eval(re.search(r"^ legend=(\[.*?\])$", gen, re.M).group(1))
leg_world = ast.literal_eval(re.search(r"^ if globalview:legend=(\[.*?\])$", gen, re.M).group(1))
m = Map('carlos', 'counterfactual', rel); s = SCEN['carlos']
src = load(rel)
ents = []
for i, f in enumerate(src['features']):
    p = f['properties']
    attrs = {k: v for k, v in p.items() if k not in ('name', 'cat', 'color', 'note')}
    ents.append(entity(m, i, rel, f['geometry'], p['name'], p['cat'], p['color'], role_v1(p, p['color']), p.get('note'), attrs,
                       'approximate' if p.get('approx') else 'generalized'))
def mono_filter(year):
    return [e for e in ents if not (year == 1556 and any(t in e['name'] for t in ['Portugal', 'portugu', 'Brasil', 'Filipinas', 'Río de la Plata']))]
# Sacro Imperio: v1 layer computed from HB 1600 minus the scenario territories, first (underneath) in every stage.
imp = V1['carlos']['frames'][0]['features'][0]
assert imp['properties']['name'].startswith('Sacro Imperio') and all(canon(fr['features'][0]['geometry']) == canon(imp['geometry']) for fr in V1['carlos']['frames'])
imperial = v1_entity(m, 'carlos', 0, 0, imp, 'hb-sacro-imperio', 'imperial')
frames = [frame(y, s['frames'][y], [imperial] + mono_filter(y)) for y in sorted(s['frames'])]
# Legend: Europe-view entries plus the colonial entries of the world view. 'frontier' has no features
# (its overlays are computed in generar.py and are not in escenario.geojson).
covers = {'aust': ['aust', 'bohem', 'royal']}
legend = [dict(key=k, label=l, color=COL[k], categories=covers.get(k, [k])) for k, l in leg_eu] + \
         [dict(key=k, label=l, color=COL[k], categories=[k]) for k, l in leg_world if k in ('escolon', 'ptcolon')]
pr_rel = 'mapas/monarquia-universal/datos/puertos_y_rutas.json'
pr = load(pr_rel)
dates = {'Manila': 1571, 'Cebú': 1565, 'Acapulco': 1565, 'Luanda': 1576, 'Río de Janeiro': 1565, 'Buenos Aires': 1580, 'Portobelo': 1597}
ports, routes = [], []
for i, p in enumerate(pr['ports']):
    start = 1565 if p['name'] in ['Manila', 'Cebú', 'Acapulco'] else 1580 if p['cat'] in ['port', 'trade', 'concession'] else 1556
    start = max(start, dates.get(p['name'], start))
    g = dict(type='Point', coordinates=[p['lon'], p['lat']])
    ports.append(dict(name=p['name'], category=p['cat'], color=COL.get(p['cat'], '#faf7ed'), gid=m.gid(g, f'{pr_rel}#ports[{i}]', f'port{i:02d}'), note=p.get('note'), start=start))
for i, r in enumerate(pr['routes']):
    start = 1565 if 'Manila' in r['name'] else 1580 if r['cat'] == 'port' else 1556
    g = dict(type='LineString', coordinates=r['coordinates'])
    routes.append(dict(name=r['name'], category=r['cat'], color=COL[r['cat']], gid=m.gid(g, f'{pr_rel}#routes[{i}]', f'route{i:02d}'),
                       note='Itinerario esquemático, no dominio del océano', start=start))
eu = [f['geometry'] for f in src['features'] if f['properties']['cat'] in ('hisp', 'port', 'burg', 'aust', 'bohem', 'royal')]
emit(m, dict(legend=legend, patterns={}, sources=s['sources'], frames=frames, ports=ports, routes=routes,
             meta=dict(extraOrigins=[pr_rel, hb_script('carlos')], derived='La capa del Sacro Imperio: ' + HB_NOTE + '.')),
     catalog_entry(m, s, sorted(s['frames']), None, legend, bounds(eu),
                   {'Europa': bounds(eu), 'Mundo': bounds([f['geometry'] for f in src['features']])}, [HB_LICENSE]))

# ======================= centrales =======================
rel = 'mapas/potencias-centrales/datos/escenario.geojson'
gen = read('mapas/potencias-centrales/generar.py')
m = Map('centrales', 'counterfactual', rel); s = SCEN['centrales']
src = load(rel)
ents = []
for i, f in enumerate(src['features']):
    p = f['properties']; c = p['color']
    pat = c[5:-1] if c.startswith('url(#') else None
    ents.append(entity(m, i, rel, f['geometry'], p['name'], p['kind'], None if pat else c, role_v1(p, c), p.get('note'), None, 'approximate', pat))
leg = ast.literal_eval(re.search(r"for j,\(col,txt\) in enumerate\((\[.*?\])\):", gen).group(1))
# Original legend groups categories by colour; this table makes the grouping explicit.
GROUP = {'#6b7880': ('centrales', ['Potencia central', 'Anexión propuesta', 'Ampliación búlgara — hipótesis', 'Reparto de 1918 simplificado']),
         '#b8c2c3': ('vinculados', ['Estado vinculado a Alemania — hipótesis']),
         '#d6b48b': ('restringida', ['Soberanía restringida — hipótesis']),
         'url(#hatch)': ('negociacion', ['Zona de negociación']),
         '#d8d2bf': ('referencia', ['Estado de referencia'])}
legend = []
for col, txt in leg:
    k, cats = GROUP[col]
    legend.append(dict(key=k, label=txt, color=None if col.startswith('url') else col, pattern='hatch' if col.startswith('url') else None, categories=cats))
assert {e['category'] for e in ents} <= {c for l in legend for c in l['categories']}
legend = [{k: v for k, v in l.items() if v is not None} for l in legend]
# 1914 and 1918 come from v1: the HB 1914 layer clipped to Europe, plus in 1918 the five eastern states of the scenario.
ref14 = hb_reference(m, 'centrales', 0, 'ref1914')
assert len(ref14) == len(V1['centrales']['frames'][0]['features'])
EAST18 = ['Finlandia', 'Ducado Báltico', 'Lituania', 'Polonia', 'Ucrania']
east18 = [e for e in ents if e['name'] in EAST18]
assert [f['properties']['name'] for f in V1['centrales']['frames'][1]['features'][len(ref14):]] == [e['name'] for e in east18]
legend.append(dict(key='ref1914', label='Capa de referencia de 1914 (historical-basemaps, colores del visor anterior)', categories=['ref1914'], original=False))
fr_c = {1914: ref14, 1918: ref14 + east18, 1920: ents, 1925: ents}
emit(m, dict(legend=legend, patterns=svg_patterns(gen, ['hatch']), sources=s['sources'], frames=[frame(y, s['frames'][y], fr_c[y]) for y in sorted(fr_c)], ports=[], routes=[],
             meta=dict(extraOrigins=[hb_script('centrales')], derived='Las etapas 1914 y 1918: ' + HB_NOTE + '.')),
     catalog_entry(m, s, sorted(fr_c), None, legend, [[29, -13], [72, 60]], {'Europa': [[29, -13], [72, 60]]}, [HB_LICENSE]))

# ======================= eje =======================
rel = 'mapas/victoria-eje/datos/escenario.geojson'
gen = read('mapas/victoria-eje/generar.py')
C = ast.literal_eval(re.search(r'^C=(\{.*?\})$', gen, re.M).group(1))
m = Map('eje', 'counterfactual', rel); s = SCEN['eje']
src = load(rel)
ents = []
for i, f in enumerate(src['features']):
    p = f['properties']
    attrs = {k: v for k, v in p.items() if k not in ('name', 'category', 'color', 'note')}
    ents.append(entity(m, i, rel, f['geometry'], p['name'], p['category'], p['color'], role_v1(p, p['color']), p.get('note'), attrs,
                       'approximate' if p.get('approx') else 'generalized', 'project' if p.get('project') else None))
leg = re.search(r"for j,\(col,label\) in enumerate\((\[.*?\])\):", gen).group(1)
leg = [(c, l) for c, l in re.findall(r"\((C\['\w+'\]|'url\(#project\)'),'([^']*)'\)", leg)]
covers = {'italy': ['italy', 'italian'], 'ally': ['ally', 'client']}
legend = []
for c, l in leg:
    if c.startswith('C['):
        k = c[3:-2]; legend.append(dict(key=k, label=l, color=C[k], categories=covers.get(k, [k])))
    else:
        legend.append(dict(key='project', label=l, pattern='project', categories=[]))
# Categories drawn in the original but absent from its legend: listed, flagged as not original.
for k, l in [('neutral', 'Otros Estados de referencia'), ('britain', 'Reino Unido'), ('russia', 'Espacio soviético o sucesor residual')]:
    legend.append(dict(key=k, label=l + ' (sin entrada en la leyenda original)', color=C[k], categories=[k], original=False))
assert {e['category'] for e in ents} <= {c for l in legend for c in l['categories']}
ref38 = hb_reference(m, 'eje', 0, 'ref1938')
assert len(ref38) == len(V1['eje']['frames'][0]['features'])
legend.append(dict(key='ref1938', label='Capa de referencia de 1938 (historical-basemaps, colores del visor anterior)', categories=['ref1938'], original=False))
fr_e = {1938: ref38, 1942: [e for e in ents if e['role'] != 'claim'], 1944: ents, 1948: ents}
emit(m, dict(legend=legend, patterns=svg_patterns(gen, ['project']), sources=s['sources'], frames=[frame(y, s['frames'][y], fr_e[y]) for y in sorted(fr_e)], ports=[], routes=[],
             meta=dict(extraOrigins=[hb_script('eje')], derived='La etapa 1938: ' + HB_NOTE + '.')),
     catalog_entry(m, s, sorted(fr_e), None, legend, [[29, -13], [72, 61]], {'Europa': [[29, -13], [72, 61]]}, [HB_LICENSE]))

# ======================= fronteras-2101 =======================
rel = 'mapas/fronteras-2100/escenario.json'
gj_rel = 'mapas/fronteras-2100/fronteras-2101.geojson'
e = load(rel); cases = {f['properties']['id']: f['properties'] for f in load(gj_rel)['features']}
md_rel = 'mapas/fronteras-2100/mapa-datos.js'
fm = json.loads(read(md_rel).split('=', 1)[1].rstrip().rstrip(';'))
levels = sorted(fm['levels'].items(), key=lambda kv: kv[1]['order'])
m = Map('fronteras-2101', 'prospective', rel)
frames = []
for fr in e['frames']:
    feats = []
    for i, f in enumerate(fr['features']):
        p = f['properties']; c = cases[p['id']]
        attrs = {k: c[k] for k in ('region', 'kind', 'current', 'outlook', 'conditions', 'central', 'number', 'levelLabel') if k in c}
        en = entity(m, i, f'{rel}#frames[{e["frames"].index(fr)}].', f['geometry'], p['name'], c['level'], p['color'], 'case', p.get('note'), attrs,
                    'generalized', None, p.get('sourceUrls'), entity_id=p['id'])
        en['certainty'] = p.get('certainty')
        feats.append(en)
    frames.append(frame(fr['year'], dict(title=fr['title'], text=fr['text'], historical=fr['historical']), feats,
                        basis='historical-reference' if fr['historical'] else 'prospective-case'))
legend = [dict(key=k, label=v['label'], color=v['color'], categories=[k]) for k, v in levels]
s = dict(e, sources=e['sources'])
emit(m, dict(legend=legend, patterns={}, sources=e['sources'], frames=frames, ports=[], routes=[],
             meta=dict(extraOrigins=[gj_rel, md_rel], asOf=fm.get('asOf'),
                       warning=read('mapas/fronteras-2100/LEEME.md').split('\n\n')[1].strip())),
     catalog_entry(m, s, [fr['year'] for fr in e['frames']], None, legend, [[-60, -180], [83, 180]], {'Mundo': [[-60, -180], [83, 180]]}, [NE_LICENSE]))

# ======================= maps generated from historical-basemaps =======================
# Six counterfactuals (build_data.py and build_extension.py) and the eight cumulative-extent maps.
# Their original legend is the v1 viewer's: roles for the counterfactuals, periods or crowns for extension.
HB_MAPS = [('japon', 'counterfactual'), ('gran-colombia', 'counterfactual'), ('kalmar', 'counterfactual'),
           ('mexico-norte', 'counterfactual'), ('centroamerica', 'counterfactual'), ('tres-naciones', 'counterfactual'),
           ('max-espana', 'extension'), ('max-portugal', 'extension'), ('max-iberia', 'extension'), ('max-britanico', 'extension'),
           ('max-frances', 'extension'), ('max-roma', 'extension'), ('max-mongol', 'extension'), ('max-otomano', 'extension')]
for sid, kind in HB_MAPS:
    sc = V1[sid]
    m = Map(sid, kind, hb_script(sid))
    if kind == 'extension':
        keys = {l['label']: f'p{i}' for i, l in enumerate(sc['legend'])}
        legend = [dict(key=f'p{i}', label=l['label'], color=l['color'], categories=[f'p{i}']) for i, l in enumerate(sc['legend'])]
        cat_of = lambda p: keys[p['period']]
    else:
        present = {f['properties']['role'] for fr in sc['frames'] for f in fr['features']}
        legend = [dict(key=r, label=l, categories=[r]) for r, l in V1_ROLES if r in present]
        cat_of = lambda p: p['role']
    frames = []
    for k, fr in enumerate(sc['frames']):
        feats = []
        for i, f in enumerate(fr['features']):
            p = f['properties']
            # extension entries can share a name (Ottoman pieces of one country), so their v1 id is the identity
            e = v1_entity(m, sid, k, i, f, p['id'] if kind == 'extension' else p['entityId'], cat_of(p))
            e['certainty'] = p['certainty']
            feats.append(e)
        assert len({e['entityId'] for e in feats}) == len(feats), (sid, fr['year'])
        frames.append(frame(fr['year'], fr, feats, basis='cumulative-extent' if kind == 'extension' else None))
    ports = [dict(name=p['name'], category=p['cat'], color=v1_port_color(p['cat']), note=p.get('note'), start=p.get('start'),
                  gid=m.gid(dict(type='Point', coordinates=[p['lon'], p['lat']]), hb_origin(sid, f'ports[{i}]'), f'port{i:02d}'))
             for i, p in enumerate(sc.get('ports', []))]
    routes = [dict(name=r['name'], category=r['cat'], color=v1_route_color(r['cat']), note='Itinerario esquemático', start=r.get('start'),
                   gid=m.gid(dict(type='LineString', coordinates=r['coordinates']), hb_origin(sid, f'routes[{i}]'), f'route{i:02d}'))
              for i, r in enumerate(sc.get('routes', []))]
    ports = [{k: v for k, v in o.items() if v is not None} for o in ports]
    routes = [{k: v for k, v in o.items() if v is not None} for o in routes]
    extra = dict(roleNames=sc['roleNames']) if kind == 'extension' else {}
    b = sc.get('bounds') or bounds(list(m.geometries.values()))
    emit(m, dict(legend=legend, patterns={}, sources=sc['sources'], frames=frames, ports=ports, routes=routes, **extra,
                 meta=dict(derived=HB_NOTE + '.', v1=dict(center=sc.get('center'), zoom=sc.get('zoom'), color=sc.get('color')))),
         catalog_entry(m, sc, [fr['year'] for fr in sc['frames']], None, legend, b, None, [HB_LICENSE]))

# ======================= land (neutral background) =======================
base = fm['base']
land = dict(schema=2, collection=dict(type='FeatureCollection', features=[dict(type='Feature', properties={}, geometry=f['geometry']) for f in base['features']]),
            source=dict(title='Natural Earth (países), base del mapa de prospectiva', path='mapas/fronteras-2100/mapa-datos.js',
                        sha256=sha_file(md_rel),
                        note='Solo fondo neutro (tierra con --land, sin fronteras). No es dato histórico.'))
(OUT / 'land.js').write_text('// Generated by atlas/build/migrar_originales.py; do not edit by hand.\nwindow.ATLAS_LAND=' + json.dumps(land, separators=(',', ':')) + ';\n', encoding='utf-8', newline='\n')

ORDER = {'history': 0, 'counterfactual': 1, 'extension': 2, 'prospective': 3}
CATALOG.sort(key=lambda c: (ORDER[c['kind']], c['years'][0]))
CATALOG = [{k: v for k, v in c.items() if v is not None} for c in CATALOG]
(OUT / 'catalog.js').write_text('// Generated by atlas/build/migrar_originales.py; do not edit by hand.\nwindow.ATLAS_CATALOG=' +
                                json.dumps(CATALOG, ensure_ascii=False, indent=0) + ';\n', encoding='utf-8', newline='\n')
(OUT / '_geometrias-origen.json').write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=0), encoding='utf-8', newline='\n')
print('catálogo:', [c['id'] for c in CATALOG])

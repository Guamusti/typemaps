"""Task 2.8: validates atlas/data against contract v2 and the originals, and writes atlas/data/MANIFEST.json
(PLAN §8, CONTRATO §10). Exit code 1 on any error.
- Geometries copied from an original: re-extracted from atlas/source-data/originales and compared by canonical hash.
- Geometries derived from historical-basemaps: the HB layers are checked against source-data/BASES.csv, the ported
  v1 generator (build/hb) is run again without simplification and its output compared by canonical hash.
- Entity counts per stage: against that regenerated v1 output and, if present, against atlas-escenarios/dist/data.
Usage: python3.12 -I -X utf8 validar.py"""
import csv, hashlib, json, os, re, sys
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[1]
DATA, ORIG = ATLAS / 'data', ATLAS / 'source-data' / 'originales'
KIND = {'history', 'counterfactual', 'extension', 'prospective'}
ROLE = {'sovereign', 'control', 'occupation', 'dependent', 'federal', 'influence', 'claim', 'project', 'case'}
CERT, PREC = {'documented', 'scenario'}, {'source', 'generalized', 'approximate', 'schematic'}
REPR = {'area', 'location-marker'}
BASIS = {'historical-reference', 'counterfactual-interpretation', 'cumulative-extent', 'prospective-case'}
# Number of entities of each original (CONTRATO §10.4): all of them must be present in some stage.
EXPECTED = {'gran-alemania': 91, 'carlos': 19, 'centrales': 80 + 37, 'eje': 95 + 47, 'fronteras-2101': 38}
# gran-alemania adds the 24 context entities that v1 dropped, so its stages differ from v1 on purpose.
EXPECTED_FRAMES_DIFFER = {'gran-alemania'}
checked_dist = []
errors = []
def err(msg): errors.append(msg)
def canon(g): return hashlib.sha256(json.dumps(g, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
def sha(b): return hashlib.sha256(b).hexdigest()

def payload(path, fn):
    s = path.read_text(encoding='utf-8')
    body = s.split('\n', 1)[1] if s.startswith('//') else s
    m = re.fullmatch(r'window\.' + fn + r'\((.*)\);\n', body, re.S)
    if not m: err(f'{path.name}: no es window.{fn}(JSON);'); return None
    return json.loads(m.group(1))

# Frozen copies must still match the originals' recorded hashes, and the HB layers their BASES.csv hashes.
for r in csv.DictReader(open(ORIG / 'MANIFEST.csv', encoding='utf-8')):
    if sha((ATLAS / r['copia']).read_bytes()) != r['sha256']: err(f'copia alterada: {r["copia"]}')
for r in csv.DictReader(open(ATLAS / 'source-data' / 'BASES.csv', encoding='utf-8')):
    if r['copiado'] == 'sí':
        b = ATLAS / 'source-data' / 'bases' / r['fichero']
        if not b.exists() or sha(b.read_bytes()) != r['sha256']: err(f'base ausente o alterada: {r["fichero"]}')

# Regenerate the HB-derived output with the ported generator, without simplification.
os.environ['ATLAS_TOLERANCE'] = 'none'
sys.path.insert(0, str(ATLAS / 'build' / 'hb'))
import comun, v1_datos, v1_extension  # noqa: E402
V1 = {s['id']: s for s in json.loads(json.dumps(v1_datos.export() + v1_extension.export(), ensure_ascii=False))}
V1_DIST = ATLAS.parents[1] / 'atlas-escenarios' / 'dist' / 'data'

_cache = {}
def original_geometry(origin):
    rel, path = origin.split('#', 1)
    if ':' in rel: _cache[rel] = V1[rel.split(':', 1)[1]]  # atlas-escenarios/scripts/<generator>.py:<scenario id>
    if rel not in _cache:
        text = (ORIG / rel).read_text(encoding='utf-8')
        if rel.endswith('.html'):
            text = re.search(r'<script[^>]+id=["\']geo["\'][^>]*>(.*?)</script>', text, re.S).group(1)
        _cache[rel] = json.loads(text)
    node = _cache[rel]
    for key, idx in re.findall(r'(\w+)\[(\d+)\]', path):
        node = node[key][int(idx)]
    if 'geometry' in node: return node['geometry']
    if 'lon' in node: return dict(type='Point', coordinates=[node['lon'], node['lat']])
    return dict(type='LineString', coordinates=node['coordinates'])

ns = {}
exec(compile((DATA / 'catalog.js').read_text(encoding='utf-8').split('\n', 1)[1].replace('window.ATLAS_CATALOG=', 'CAT=', 1).rstrip().rstrip(';'), 'catalog', 'exec'), {'true': True, 'false': False, 'null': None}, ns)
catalog = ns['CAT']
origins = json.loads((DATA / '_geometrias-origen.json').read_text(encoding='utf-8'))
manifest = dict(files={}, geometries={}, roleTables={}, summary={})
for c in catalog:
    mid = c['id']
    if c['kind'] not in KIND: err(f'{mid}: kind {c["kind"]}')
    raw = (DATA / c['file']).read_bytes()
    if sha(raw) != c['dataSha256']: err(f'{mid}: dataSha256 no coincide')
    d = payload(DATA / c['file'], 'ATLAS_REGISTER')
    if d is None: continue
    geoms = d.get('geometries')
    if 'geoFile' in c:
        g = payload(DATA / c['geoFile'], 'ATLAS_REGISTER_GEO')
        if sha((DATA / c['geoFile']).read_bytes()) != c.get('geoSha256'): err(f'{mid}: geoSha256 no coincide')
        geoms = g['geometries']
    if d['schema'] != 2 or d['id'] != mid or d['kind'] != c['kind']: err(f'{mid}: cabecera')
    years = [fr['year'] for fr in d['frames']]
    if years != sorted(years) or years != c['years']: err(f'{mid}: años {years} vs {c["years"]}')
    cats = {x for l in d['legend'] for x in l.get('categories', [l['key']])}
    for k, gm in geoms.items():
        h = canon(gm)
        if k != 'g-' + h[:16]: err(f'{mid}: gid {k} no es su hash')
        o = origins[mid].get(k)
        if not o: err(f'{mid}: {k} sin origen'); continue
        if canon(original_geometry(o['origin'])) != h: err(f'{mid}: {k} difiere del original {o["origin"]}')
        manifest['geometries'][f'{mid}/{k}'] = dict(o, map=mid)
    used, entities, markers = set(), set(), 0
    for fr in d['frames']:
        if fr['basis'] not in BASIS: err(f'{mid} {fr["year"]}: basis')
        ids = [f['id'] for f in fr['features']]
        if len(ids) != len(set(ids)): err(f'{mid} {fr["year"]}: ids repetidos')
        for f in fr['features']:
            g = geoms.get(f['gid'])
            if g is None: err(f'{mid} {f["id"]}: gid sin geometría'); continue
            used.add(f['gid']); entities.add(f['entityId'])
            if f['category'] not in cats: err(f'{mid} {f["id"]}: category {f["category"]} fuera de la leyenda')
            if f['role'] not in ROLE or f['certainty'] not in CERT or f['precision'] not in PREC or f['representation'] not in REPR:
                err(f'{mid} {f["id"]}: vocabulario')
            point = g['type'] in ('Point', 'MultiPoint')
            if point != (f['representation'] == 'location-marker'): err(f'{mid} {f["id"]}: marcador/área')
            markers += point
            if f.get('pattern') and f['pattern'] not in d.get('patterns', {}): err(f'{mid} {f["id"]}: trama {f["pattern"]}')
            if f.get('color') and not re.fullmatch(r'#[0-9a-f]{6}', f['color']): err(f'{mid} {f["id"]}: color')
            if not f.get('color') and not f.get('pattern'): err(f'{mid} {f["id"]}: sin color ni trama')
            for u in f.get('sourceUrls', []):
                if not u.startswith('https://'): err(f'{mid} {f["id"]}: URL {u}')
    for o in d.get('ports', []) + d.get('routes', []):
        used.add(o['gid'])
        if o['gid'] not in geoms: err(f'{mid}: overlay sin geometría')
    if set(geoms) - used: err(f'{mid}: geometrías sin usar')
    if EXPECTED.get(mid) is not None and len(entities) != EXPECTED[mid]: err(f'{mid}: {len(entities)} entidades, se esperaban {EXPECTED[mid]}')
    counts = {fr['year']: len(fr['features']) for fr in d['frames']}
    if mid in V1 and mid not in EXPECTED_FRAMES_DIFFER:
        if counts != {fr['year']: len(fr['features']) for fr in V1[mid]['frames']}: err(f'{mid}: recuento por etapa distinto del generador v1')
        if (V1_DIST / f'{mid}.json').exists():
            ref = json.loads((V1_DIST / f'{mid}.json').read_text(encoding='utf-8'))
            if counts != {fr['year']: len(fr['features']) for fr in ref['frames']}: err(f'{mid}: recuento por etapa distinto de atlas-escenarios/dist')
            else: checked_dist.append(mid)
    for s in d['sources'] + c['sources']:
        if not s['url'].startswith('https://'): err(f'{mid}: fuente {s["url"]}')
    manifest['roleTables'][mid] = ('case (CONTRATO §8.4)' if c['kind'] == 'prospective' else
                                   'provisional (regla v1 de build_data.py)' if mid in ('gran-alemania', 'carlos', 'centrales', 'eje') else
                                   'provisional (rol fijado por el generador v1, sin revisar por R2)')
    manifest['summary'][mid] = dict(frames={fr['year']: len(fr['features']) for fr in d['frames']}, entities=len(entities),
                                    geometries=len(geoms), markers=markers, pendingYears=c.get('pendingYears'))
for p in sorted(DATA.iterdir()):
    if p.is_file() and p.name != 'MANIFEST.json': manifest['files'][p.name] = sha(p.read_bytes())
if comun.REPAIRS: manifest['repairs'] = comun.REPAIRS
(DATA / 'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
for mid, s in manifest['summary'].items(): print(mid, s)
print(len(manifest['geometries']), 'geometrías comprobadas contra el original;', len(comun.REPAIRS), 'reparaciones;',
      'recuentos iguales a atlas-escenarios/dist en', len(checked_dist), 'mapas;', len(errors), 'errores')
for e in errors[:50]: print('ERROR', e)
sys.exit(1 if errors else 0)

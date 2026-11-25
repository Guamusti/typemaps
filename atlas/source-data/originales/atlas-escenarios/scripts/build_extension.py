"""Mapas de «máxima extensión acumulada»: todo territorio que un poder controló alguna vez,
aunque no fuera a la vez o su presencia fuese breve o nominal.

Independiente de build_data.py: escribe sus propios archivos y data/catalog-extension.js,
que añade sus entradas al catálogo principal en el navegador.

Uso:  python scripts/build_extension.py
Fuentes cartográficas: aourednik/historical-basemaps (source-data/hb y ../mapas/*/datos).
"""
import sys, json, copy, hashlib, re
from pathlib import Path
SITE = Path(__file__).resolve().parents[1]; ROOT = SITE.parent; OUT = SITE / 'dist/data'
sys.path.insert(0, str(ROOT / 'mapas/potencias-centrales/.libs'))
from shapely.geometry import shape, mapping, box, Point
from shapely.ops import unary_union
from shapely import make_valid

# ── Cartografía base ──────────────────────────────────────────────────────────
HB_DIRS = [SITE / 'source-data/hb', SITE / 'source-data', ROOT / 'mapas/monarquia-universal/datos',
           ROOT / 'mapas/potencias-centrales/datos', ROOT / 'mapas/victoria-eje/datos']
_cache = {}
def hb(year):
    if year not in _cache:
        for d in HB_DIRS:
            p = d / f'world_{year}.geojson'
            if p.exists():
                fc = json.loads(p.read_text(encoding='utf-8'))
                _cache[year] = [(f['properties'], make_valid(shape(f['geometry'])).buffer(0)) for f in fc['features'] if f.get('geometry')]
                break
        else:
            raise FileNotFoundError(f'world_{year}.geojson')
    return _cache[year]

def _clip(g, clip):
    return g.intersection(box(*clip)) if clip else g

# Especificaciones geométricas
def M(*names, clip=None): return ('hbname', 1994, names, clip)          # país en 1994
def H(year, *names, clip=None): return ('hbname', year, names, clip)    # entidad histórica por NAME
def S(year, *subjects, clip=None): return ('hbsubj', year, subjects, clip)  # por SUBJECTO
def P(lon, lat): return ('pt', lon, lat)
def U(*specs): return ('union', specs)
def D(a, b): return ('diff', a, b)  # a menos b
def I(a, b): return ('intersect', a, b)

def resolve(spec):
    kind = spec[0]
    if kind == 'pt': return Point(spec[1], spec[2])
    if kind == 'union': return unary_union([resolve(s) for s in spec[1]])
    if kind == 'diff': return resolve(spec[1]).difference(resolve(spec[2]))
    if kind == 'intersect': return resolve(spec[1]).intersection(resolve(spec[2]))
    _, year, names, clip = spec
    key = 'NAME' if kind == 'hbname' else 'SUBJECTO'
    pats = [re.compile('^' + n + '$', re.I) for n in names]
    geoms = [g for p, g in hb(year) if p.get(key) and any(r.match(p[key]) for r in pats)]
    if not geoms: raise ValueError(f'Sin geometría para {spec}')
    return _clip(unary_union(geoms), clip)

def simplify(g):
    if g.geom_type in ('Point', 'MultiPoint'): return mapping(g)
    return mapping(make_valid(g).buffer(0).simplify(.018, preserve_topology=True))

def yl(y): return f'{-y} a. C.' if y < 0 else str(y)
def span(a, b): return f'{yl(a)}–{yl(b) if b else "hoy"}'

def E(name, start, end, spec, role='sovereign', note='', within=None, group=None):
    return dict(name=name, start=start, end=end, spec=spec, role=role, note=note, within=within, group=group)

ROLE_NAMES = {
    'sovereign': 'Dominio efectivo',
    'dependent': 'Vasallaje o protectorado',
    'occupation': 'Ocupación o campaña',
    'influence': 'Enclave o presencia breve',
    'claim': 'Soberanía nominal',
}

def build(cfg):
    extents = {k: resolve(v) for k, v in cfg.get('extents', {}).items()}
    entries = sorted(cfg['entries'], key=lambda e: e['start'])
    # Una relación fuerte (dominio, vasallaje) se superpone a otra débil anterior;
    # una débil solo ocupa lo que aún no estaba en el mapa.
    strong = None; every = None; feats = []
    for e in entries:
        g = resolve(e['spec'])
        if g.geom_type not in ('Point', 'MultiPoint'):
            g = make_valid(g).buffer(0)
            if e['within']: g = g.intersection(extents[e['within']])
            is_strong = e['role'] in ('sovereign', 'dependent')
            prev = strong if is_strong else every
            if prev is not None: g = g.difference(prev)
            if g.is_empty or g.area < .01:
                print('  - sin superficie nueva:', e['name']); continue
            every = g if every is None else unary_union([every, g])
            if is_strong: strong = g if strong is None else unary_union([strong, g])
        if cfg.get('colorBy') == 'group':
            label, color = cfg['groups'][e['group']]
        else:
            label, color = next((l, c) for top, l, c in cfg['periods'] if e['start'] <= top)
        note = f"{span(e['start'], e['end'])} · {e['note'] or label}."
        feats.append(dict(type='Feature', geometry=simplify(g), properties=dict(
            name=e['name'], color=color, role=e['role'], note=note, certainty='documented', approx=True,
            start=e['start'], end=e['end'], period=label)))
    frames = []
    for i, (year, title, text) in enumerate(cfg['cuts']):
        last = i == len(cfg['cuts']) - 1
        fs = []
        for f in feats:
            p = f['properties']
            if p['start'] > year: continue
            f = copy.deepcopy(f)
            lost = (not last) and p['end'] is not None and p['end'] < year
            if lost: f['properties']['lost'] = True
            fs.append(f)
        frames.append(dict(year=year, title=title, text=text, features=fs, historical=True))
    legend = [dict(color=c, label=l) for l, c in cfg['groups'].values()] if cfg.get('colorBy') == 'group' else [dict(color=c, label=l) for _, l, c in cfg['periods']]
    sc = {k: v for k, v in cfg.items() if k not in ('entries', 'cuts', 'periods', 'groups', 'extents', 'colorBy')}
    sc.update(kind='extension', frames=frames, legend=legend, roleNames=ROLE_NAMES, ports=[], routes=[])
    for fr in sc['frames']:
        for f in fr['features']:
            p = f['properties']
            p['id'] = sc['id'] + '-' + hashlib.sha256((p['name'] + str(p['start']) + json.dumps(f['geometry'], separators=(',', ':'))).encode()).hexdigest()[:14]
            p['validAt'] = fr['year']
            p['representation'] = 'location-marker' if f['geometry']['type'] in ('Point', 'MultiPoint') else 'area'
    n_areas = sum(1 for f in feats if f['geometry']['type'] not in ('Point', 'MultiPoint'))
    print(f"{sc['id']}: {len(feats)} entradas ({n_areas} áreas), {len(frames)} etapas")
    return sc

def src(t, u): return dict(title=t, url=u)
HBSRC = src('Historical Basemaps (cartografía base por años)', 'https://github.com/aourednik/historical-basemaps')

C6 = ['#f6c453', '#f08a4b', '#e0569b', '#a06cff', '#5b8cff', '#2bb5a6']

# ══ 1. Imperio español ════════════════════════════════════════════════════════
SPAIN = [
    E('Coronas de Castilla y Aragón', 1479, None, M('Spain'), note='Núcleo peninsular e insular de la Monarquía; Navarra se incorpora en 1512'),
    E('Rosellón y Cerdaña', 1493, 1659, M('France', clip=(1.7, 42.3, 3.2, 42.95)), note='Cedidos a Francia en la Paz de los Pirineos'),
    E('Reino de Sicilia', 1479, 1713, H(1530, 'Sicily'), note='Herencia aragonesa; cedido en Utrecht'),
    E('Reino de Cerdeña', 1479, 1714, H(1530, 'Sardinia'), note='Herencia aragonesa; pasa a Austria y luego a Saboya'),
    E('Malta', 1479, 1530, M('Malta'), note='Dependiente de Sicilia hasta su cesión a la Orden de San Juan'),
    E('Reino de Nápoles', 1504, 1714, H(1530, 'Naples'), note='Conquistado por el Gran Capitán'),
    E('Ducado de Milán', 1535, 1714, H(1600, 'Milan'), note='Pieza clave del Camino Español'),
    E('Estado de los Presidios', 1557, 1707, P(11.2, 42.44), 'influence', 'Enclaves costeros toscanos (Orbetello, Porto Ercole)'),
    E('Países Bajos de los Habsburgo', 1556, 1714, H(1600, 'Habsburg Netherlands'), note='Las Provincias Unidas del norte se separan de hecho desde 1581 (reconocido en 1648)'),
    E('Franco Condado', 1556, 1678, H(1650, 'Franche.*'), note='Perdido en la Paz de Nimega'),
    E('Inglaterra e Irlanda · Felipe rey consorte', 1554, 1558, M('United Kingdom', 'Ireland'), 'influence', 'Felipe II comparte el título real con María Tudor; sin gobierno español'),
    E('Bretaña · guarnición de Blavet', 1590, 1598, P(-3.35, 47.73), 'occupation', 'Intervención en las guerras de religión francesas'),
    E('Reino de Portugal', 1580, 1640, M('Portugal'), 'dependent', 'Unión dinástica: Portugal conserva leyes, cortes y administración propias'),
    E('Brasil portugués', 1580, 1640, H(1650, 'Portuguese Brazil'), 'dependent', 'Bajo la unión ibérica; franja costera efectiva'),
    E('Goa', 1580, 1640, P(73.85, 15.45), 'dependent', 'Estado de la India portugués durante la unión'),
    E('Malaca', 1580, 1640, P(102.25, 2.2), 'dependent', 'Portuguesa durante la unión; tomada por los neerlandeses en 1641'),
    E('Macao', 1580, 1640, P(113.55, 22.19), 'dependent', 'Enclave portugués durante la unión'),
    E('Luanda', 1580, 1640, P(13.23, -8.84), 'dependent', 'Enclave portugués de Angola durante la unión'),
    E('Ormuz', 1580, 1622, P(56.45, 27.1), 'dependent', 'Fortaleza portuguesa perdida ante Persia e Inglaterra'),
    E('La Española · Santo Domingo', 1492, 1821, M('Dominican Republic'), note='Primera colonia; cedida a Francia de 1795 a 1809 y de nuevo española 1861–1865'),
    E('La Española · parte occidental', 1492, 1697, M('Haiti'), note='Cedida a Francia en Ryswick (Saint-Domingue)'),
    E('Puerto Rico', 1508, 1898, M('Puerto Rico')),
    E('Jamaica', 1509, 1655, M('Jamaica'), note='Conquistada por Inglaterra'),
    E('Cuba', 1511, 1898, M('Cuba'), note='Con la ocupación británica de La Habana en 1762–1763'),
    E('Trinidad', 1498, 1797, M('Trinidad'), note='Ocupada por Gran Bretaña'),
    E('Castilla del Oro · Panamá', 1510, 1821, M('Panama')),
    E('Nueva España · México central', 1521, 1821, M('Mexico'), note='Virreinato de Nueva España; el norte árido con presencia dispersa'),
    E('Capitanía General de Guatemala', 1524, 1821, M('Guatemala', 'El Salvador', 'Honduras', 'Nicaragua', 'Costa Rica')),
    E('Belice · reclamación', 1525, 1798, M('Belize'), 'claim', 'Soberanía española disputada por asentamientos británicos'),
    E('Venezuela', 1522, 1823, M('Venezuela')),
    E('Nueva Granada', 1525, 1819, M('Colombia')),
    E('Perú', 1532, 1824, M('Peru'), note='Núcleo del virreinato del Perú'),
    E('Quito', 1534, 1822, M('Ecuador')),
    E('Charcas · Alto Perú', 1538, 1825, M('Bolivia')),
    E('Paraguay', 1537, 1811, M('Paraguay')),
    E('Chile central', 1541, 1818, M('Chile', clip=(-76, -38.5, -66, -17)), note='La Araucanía, al sur del Biobío, quedó fuera del control efectivo'),
    E('Río de la Plata y Tucumán', 1536, 1816, M('Argentina', clip=(-74, -38.5, -53, -21)), note='Gobernaciones y virreinato del Río de la Plata (1776)'),
    E('Banda Oriental', 1680, 1814, M('Uruguay'), note='Disputada con Portugal (Colonia del Sacramento); Montevideo en 1724'),
    E('Patagonia y Araucanía', 1544, 1816, U(M('Argentina', clip=(-76, -56, -53, -38.5)), M('Chile', clip=(-80, -56, -66, -38.5))), 'claim', 'Reclamada; pueblos indígenas independientes y fuertes aislados'),
    E('Florida', 1565, 1821, H(1715, 'Florida.*'), note='Británica entre 1763 y 1783'),
    E('Santa Elena', 1566, 1587, P(-80.68, 32.31), 'influence', 'Capital de la Florida en la actual Carolina del Sur'),
    E('Septentrión novohispano', 1598, 1821, H(1783, 'Viceroyalty of New Spain'), 'claim', 'Nuevo México, Texas, Arizona y Alta California: misiones y presidios dispersos'),
    E('Luisiana', 1762, 1801, H(1715, 'Louisiana'), note='Recibida de Francia y devuelta en San Ildefonso'),
    E('Pacífico noroeste · reclamación', 1774, 1819, U(M('United States', clip=(-125, 42, -111, 49)), M('Canada', clip=(-134, 48.2, -120, 56))), 'claim', 'Expediciones hasta Alaska; renuncia en el Tratado Adams-Onís'),
    E('Nutca', 1789, 1795, P(-126.6, 49.6), 'influence', 'Fuerte de San Miguel en la isla de Vancouver'),
    E('Filipinas', 1565, 1898, M('Philippines'), note='El sultanato de Joló y el interior de Mindanao, solo en parte sometidos'),
    E('Formosa española', 1626, 1642, M('Taiwan', clip=(120.9, 24.6, 122.1, 25.4)), 'influence', 'Fuertes de Keelung y Tamsui; expulsados por los neerlandeses'),
    E('Molucas · Ternate y Tidore', 1606, 1663, P(127.38, 0.79), 'influence', 'Guarniciones en las islas de las especias'),
    E('Islas Marianas', 1668, 1899, P(144.75, 13.45), note='Guam, vendidas o cedidas tras 1898'),
    E('Islas Palaos', 1885, 1899, P(134.5, 7.5), note='Vendidas a Alemania en 1899'),
    E('Islas Carolinas', 1886, 1899, P(158.2, 6.9), note='Vendidas a Alemania en 1899'),
    E('Melilla', 1497, None, P(-2.94, 35.29), note='Plaza de soberanía'),
    E('Peñón de Vélez de la Gomera', 1508, None, P(-4.30, 35.17), note='Perdido de 1522 a 1564'),
    E('Mazalquivir y Orán', 1505, 1792, P(-0.64, 35.70), note='Perdidos de 1708 a 1732'),
    E('Bugía', 1510, 1555, P(5.08, 36.75), 'influence', 'Presidio norteafricano'),
    E('Peñón de Argel', 1510, 1529, P(3.06, 36.79), 'influence', 'Fortaleza frente a Argel'),
    E('Trípoli', 1510, 1530, P(13.18, 32.9), 'influence', 'Cedida a la Orden de San Juan'),
    E('La Goleta y Túnez', 1535, 1574, P(10.3, 36.82), 'influence', 'Tras la jornada de Túnez de Carlos V'),
    E('Ceuta', 1580, None, P(-5.32, 35.89), note='Portuguesa hasta 1640; permanece con España (1668)'),
    E('Larache', 1610, 1689, P(-6.15, 35.19), 'influence', 'Plaza atlántica'),
    E('La Mámora', 1614, 1681, P(-6.65, 34.32), 'influence', 'Plaza atlántica'),
    E('Islas Chafarinas', 1847, None, P(-2.43, 35.18)),
    E('Fernando Poo y Annobón', 1778, 1968, M('Equatorial Guinea', clip=(5, -2, 9.2, 4)), note='Cedidas por Portugal; ocupación efectiva desde 1843'),
    E('Río Muni', 1900, 1968, M('Equatorial Guinea', clip=(9.2, 0.8, 11.5, 2.4)), note='Guinea Española continental'),
    E('Ifni', 1860, 1969, M('Morocco', clip=(-10.35, 29.1, -9.95, 29.55)), note='Ocupación efectiva desde 1934'),
    E('Sáhara Español', 1884, 1976, M('Western Sahara'), note='Río de Oro y Saguia el Hamra'),
    E('Cabo Juby · Tarfaya', 1916, 1958, M('Morocco', clip=(-13.2, 27.66, -8.67, 28.7)), 'dependent', 'Zona sur del protectorado'),
    E('Protectorado de Marruecos', 1912, 1956, H(1914, 'Spanish Morocco'), 'dependent', 'Zona norte; Tetuán ya ocupado en 1860–1862'),
    E('Tánger', 1940, 1945, P(-5.81, 35.77), 'occupation', 'Ocupación de la zona internacional durante la Segunda Guerra Mundial'),
    E('Cochinchina · Turana', 1858, 1862, P(108.2, 16.07), 'occupation', 'Expedición franco-española'),
]
SP_CUTS = [(1500, 'Los Reyes Católicos', 'Castilla y Aragón, las islas italianas de la Corona de Aragón y las primeras Antillas.'),
           (1556, 'La herencia de Carlos V', 'Italia, Flandes, la conquista de México y Perú y los presidios norteafricanos.'),
           (1600, 'La monarquía de Felipe II', 'La unión con Portugal suma su red de enclaves; Filipinas y Florida entran en el mapa.'),
           (1700, 'El final de los Austrias', 'Pérdidas en Europa (Rosellón, Franco Condado) y nuevas reclamaciones americanas.'),
           (1800, 'El apogeo borbónico', 'La Luisiana, la expansión hacia California y el Pacífico noroeste.'),
           (1900, 'Tras las independencias', 'Solo quedan las Antillas, Filipinas, Guinea y las plazas africanas; 1898 cierra el siglo.'),
           (1976, 'Todos los territorios', 'Acumulado completo: cada territorio controlado alguna vez, con su presencia efectiva o nominal.')]
SP_PER = [(1516, 'Reyes Católicos (hasta 1516)', C6[0]), (1599, 'Siglo XVI', C6[1]), (1699, 'Siglo XVII', C6[2]),
          (1799, 'Siglo XVIII', C6[3]), (1899, 'Siglo XIX', C6[4]), (9999, 'Siglo XX', C6[5])]
spain = dict(id='max-espana', title='Todo lo que fue español', subtitle='La Monarquía Hispánica, sumada en el tiempo', era='1479 – 1976',
    region='Mundo', divergence=1479, color='#f0b44c', center=[20, -20], zoom=2, world=True, bounds=[[-50, -130], [62, 160]],
    tags=['Imperio español', 'Extensión acumulada'],
    summary='Todos los territorios que estuvieron alguna vez bajo la Corona española, aunque no coincidieran en el tiempo: de Flandes a Formosa y de Nutca a Fernando Poo. El color indica el siglo de incorporación; el trazo, la intensidad del dominio.',
    limits='Mapa acumulado, no una instantánea: nunca existió a la vez. Contornos modernos o generalizados; las regiones con presencia dispersa (Septentrión, Patagonia) se marcan como soberanía nominal. Los puntos señalan presidios y enclaves sin territorio interior.',
    sources=[HBSRC, src('Monarquía Hispánica · Real Academia de la Historia', 'https://dbe.rah.es/'),
             src('Presidios del norte de África · Biblioteca Virtual de Defensa', 'https://bibliotecavirtual.defensa.gob.es/'),
             src('Tratado Adams-Onís (1819) · Avalon Project', 'https://avalon.law.yale.edu/19th_century/sp1819.asp')],
    entries=SPAIN, cuts=SP_CUTS, periods=SP_PER)

# ══ 2. Imperio portugués ══════════════════════════════════════════════════════
PORT = [
    E('Reino de Portugal', 1415, None, M('Portugal'), note='Con Madeira (1420) y Azores (1432)'),
    E('Ceuta', 1415, 1640, P(-5.32, 35.89), note='Pasa a España tras la Restauración'),
    E('Alcazarseguir', 1458, 1550, P(-5.55, 35.85), 'influence', 'Plaza marroquí'),
    E('Arcila', 1471, 1550, P(-6.03, 35.46), 'influence', 'Plaza marroquí'),
    E('Tánger', 1471, 1661, P(-5.81, 35.78), note='Dote de Catalina de Braganza a Inglaterra'),
    E('Mazagán', 1502, 1769, P(-8.5, 33.25), 'influence', 'Última plaza portuguesa en Marruecos'),
    E('Safí y Agadir', 1505, 1541, P(-9.24, 32.3), 'influence', 'Plazas atlánticas marroquíes'),
    E('Cabo Verde', 1462, 1975, P(-23.5, 15.1)),
    E('Santo Tomé y Príncipe', 1470, 1975, P(6.6, 0.3)),
    E('Fernando Poo y Annobón', 1474, 1778, M('Equatorial Guinea', clip=(5, -2, 9.2, 4)), 'claim', 'Cedidas a España en El Pardo'),
    E('San Jorge de la Mina', 1482, 1637, P(-1.35, 5.08), 'influence', 'Factoría del oro; tomada por los neerlandeses'),
    E('Guinea portuguesa', 1588, 1974, M('Guinea-Bissau'), note='Factorías de Cacheu y Bissau; interior desde finales del XIX'),
    E('Ajudá', 1721, 1961, P(2.08, 6.36), 'influence', 'Fuerte de São João Baptista'),
    E('Angola', 1575, 1975, M('Angola'), note='Costa desde 1575; el interior, a partir de las campañas de 1880–1920'),
    E('Mozambique', 1505, 1975, M('Mozambique'), note='Factorías costeras; el interior, desde el siglo XIX'),
    E('Mombasa', 1593, 1698, P(39.66, -4.06), 'influence', 'Fuerte Jesús'),
    E('Mascate', 1507, 1650, P(58.59, 23.61), 'influence', 'Plaza del golfo de Omán'),
    E('Ormuz', 1515, 1622, P(56.45, 27.1), 'influence', 'Llave del golfo Pérsico'),
    E('Baréin', 1521, 1602, P(50.6, 26.2), 'influence', 'Tributario de Ormuz'),
    E('Goa', 1510, 1961, M('India', clip=(73.65, 14.9, 74.35, 15.8)), note='Capital del Estado de la India'),
    E('Damán y Diu', 1535, 1961, U(P(72.85, 20.4), P(70.98, 20.71)), note='Plazas de Gujarat'),
    E('Bombay', 1534, 1661, P(72.83, 18.95), 'influence', 'Dote a Inglaterra en 1661'),
    E('Cochín', 1503, 1663, P(76.25, 9.96), 'influence', 'Primera fortaleza portuguesa en la India'),
    E('Hugli', 1579, 1632, P(88.4, 22.9), 'influence', 'Factoría en Bengala'),
    E('Ceilán costero', 1597, 1658, M('Sri Lanka'), 'claim', 'Litoral portugués; el reino de Kandy, independiente'),
    E('Malaca', 1511, 1641, P(102.25, 2.2), note='Tomada por los neerlandeses'),
    E('Ternate', 1522, 1575, P(127.38, 0.79), 'influence', 'Fortaleza en las Molucas'),
    E('Timor portugués', 1702, 1975, M('Indonesia', clip=(124.9, -9.6, 127.4, -8.1)), note='Presencia desde 1515; gobierno desde 1702'),
    E('Macao', 1557, 1999, P(113.55, 22.19), note='Devuelto a China en 1999'),
    E('Nagasaki', 1580, 1587, P(129.87, 32.75), 'influence', 'Cedida a los jesuitas; centro del comercio luso-japonés'),
    E('Brasil', 1500, 1822, M('Brazil'), note='Costa desde 1532; el interior, por bandeirantes y tratados (1750)'),
    E('Colonia del Sacramento', 1680, 1777, P(-57.84, -34.47), note='Disputada con España'),
    E('Provincia Cisplatina', 1817, 1828, M('Uruguay'), note='Anexionada al Reino Unido de Portugal y luego al Imperio de Brasil'),
    E('Guayana Francesa', 1809, 1817, M('French Guiana'), 'occupation', 'Ocupación luso-británica durante las guerras napoleónicas'),
    E('Olivenza', 1297, 1801, P(-7.1, 38.68), note='Cedida a España en Badajoz'),
]
PT_CUTS = [(1460, 'Ceuta y el Atlántico', 'Primeras plazas marroquíes y archipiélagos atlánticos.'),
           (1520, 'La ruta de la India', 'Factorías desde Guinea hasta Malaca: un imperio de puertos.'),
           (1600, 'El apogeo del Estado de la India', 'Ormuz, Goa, Macao y Nagasaki; el Brasil azucarero.'),
           (1700, 'Pérdidas en Oriente', 'Los neerlandeses toman Malaca, Ceilán y la costa del Malabar.'),
           (1822, 'Brasil, centro del imperio', 'La corte en Río y la Cisplatina; Brasil se independiza en 1822.'),
           (1999, 'Todos los territorios', 'Acumulado completo hasta la entrega de Macao en 1999.')]
PT_PER = [(1499, 'Siglo XV', C6[0]), (1599, 'Siglo XVI', C6[1]), (1699, 'Siglo XVII', C6[2]),
          (1799, 'Siglo XVIII', C6[3]), (9999, 'Siglo XIX en adelante', C6[4])]
portugal = dict(id='max-portugal', title='Todo lo que fue portugués', subtitle='Un imperio de puertos y rutas', era='1415 – 1999',
    region='Mundo', divergence=1415, color='#3fae7a', center=[0, 20], zoom=2, world=True, bounds=[[-40, -80], [45, 150]],
    tags=['Imperio portugués', 'Extensión acumulada'],
    summary='Todas las plazas, factorías y colonias que tuvo Portugal entre la toma de Ceuta y la entrega de Macao. Un imperio sobre todo costero, de puertos más que de territorios.',
    limits='Mapa acumulado. Muchas colonias africanas solo tuvieron control interior tras 1880–1920; se usan contornos modernos. Los puntos son fortalezas y factorías sin territorio interior.',
    sources=[HBSRC, src('Instituto Camões · historia de la expansión', 'https://www.instituto-camoes.pt/'),
             src('Portugal y el mundo · Smithsonian', 'https://asia.si.edu/whats-on/exhibitions/encompassing-the-globe-portugal-and-the-world-in-the-16th-and-17th-centuries/')],
    entries=PORT, cuts=PT_CUTS, periods=PT_PER)

# ══ 3. Monarquías ibéricas juntas ════════════════════════════════════════════
def regroup(entries, group):
    out = []
    for e in entries:
        if group == 'es' and e['start'] == 1580 and e['end'] in (1622, 1640) and e['role'] == 'dependent': continue  # ya están en la lista portuguesa
        e = dict(e, group=group); out.append(e)
    return out
iberia = dict(id='max-iberia', title='Los dos imperios ibéricos', subtitle='España y Portugal, sobre un mismo mapa', era='1415 – 1999',
    region='Mundo', divergence=1415, color='#d07a58', center=[10, -10], zoom=2, world=True, bounds=[[-50, -130], [62, 160]],
    tags=['Unión Ibérica', 'Extensión acumulada'],
    summary='Superpone todo lo que alguna vez fue español y todo lo que fue portugués. Entre 1580 y 1640 ambos imperios compartieron rey: la mayor red territorial de la Edad Moderna.',
    limits='Mapa acumulado de dos coronas; donde ambos coincidieron (Ceuta, Fernando Poo, la Banda Oriental) prevalece la primera incorporación. Contornos generalizados.',
    sources=spain['sources'] + portugal['sources'][1:],
    entries=regroup(SPAIN, 'es') + regroup(PORT, 'pt'), colorBy='group',
    groups={'es': ('Corona española', '#f0b44c'), 'pt': ('Corona portuguesa', '#3fae7a')},
    cuts=[(1500, 'Tordesillas', 'El reparto del océano: Castilla hacia el oeste, Portugal hacia el este.'),
          (1580, 'Dos imperios en expansión', 'América española, Estado de la India portugués.'),
          (1640, 'La unión de coronas', 'Felipe II, III y IV reinan sobre ambos imperios.'),
          (1800, 'El final del siglo XVIII', 'Brasil interior, Luisiana, California y el Plata.'),
          (1999, 'Todos los territorios', 'Acumulado completo de ambas coronas.')])

# ══ 4. Imperio británico ══════════════════════════════════════════════════════
BRIT = [
    E('Gran Bretaña', 1603, None, M('United Kingdom'), note='Unión de coronas (1603) y Reino de Gran Bretaña (1707)'),
    E('Irlanda', 1541, 1922, M('Ireland'), note='Reino de Irlanda y, desde 1801, Reino Unido'),
    E('Terranova', 1583, 1949, M('Canada', clip=(-60, 46.5, -52, 52)), note='Pasa a Canadá en 1949'),
    E('Bermudas', 1612, None, P(-64.75, 32.3)),
    E('Trece Colonias', 1607, 1783, M('United States', clip=(-85, 30.6, -66, 47.6)), note='Desde Jamestown hasta la independencia'),
    E('Barbados', 1627, 1966, M('Barbados')),
    E('Antillas menores británicas', 1623, 1983, M('Antigua and Barbuda', 'Saint Kitts and Nevis', 'Montserrat', 'Anguilla', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Grenada', 'Dominica', 'Turks and Caicos Islands'), note='Islas de soberanía cambiante con Francia hasta 1814'),
    E('Bahamas', 1648, 1973, M('Bahamas')),
    E('Jamaica', 1655, 1962, M('Jamaica')),
    E('Costa de los Mosquitos', 1655, 1860, M('Nicaragua', 'Honduras', clip=(-84.3, 10.9, -83.1, 15.9)), 'dependent', 'Protectorado sobre el reino misquito'),
    E('Belice', 1638, 1981, M('Belize'), note='Asentamiento maderero; colonia en 1862'),
    E('Tierra de Rupert y Canadá', 1670, 1931, M('Canada'), note='Compañía de la Bahía de Hudson; Nueva Francia en 1763; dominio en 1867'),
    E('Santa Elena', 1659, None, P(-5.7, -15.95)),
    E('Gibraltar', 1704, None, P(-5.35, 36.14)),
    E('Menorca', 1708, 1802, P(4.0, 39.95), note='Con interrupciones francesas y españolas'),
    E('Bengala y la India británica', 1757, 1947, M('India', 'Pakistan', 'Bangladesh'), note='Compañía de las Indias Orientales desde Plassey; Raj desde 1858'),
    E('Florida británica', 1763, 1783, M('United States', clip=(-87.6, 24.5, -80, 31)), note='Devuelta a España'),
    E('Reserva india y país de Ohio', 1763, 1783, M('United States', clip=(-91.5, 30.6, -85, 49)), 'claim', 'Territorio reservado a los pueblos indígenas por la Proclamación de 1763'),
    E('La Habana', 1762, 1763, P(-82.36, 23.13), 'occupation', 'Ocupación durante la guerra de los Siete Años'),
    E('Manila', 1762, 1764, P(120.98, 14.6), 'occupation', 'Ocupación durante la guerra de los Siete Años'),
    E('Nueva Gales del Sur y Australia', 1788, 1901, M('Australia'), note='Colonias federadas en 1901'),
    E('Ceilán', 1796, 1948, M('Sri Lanka')),
    E('Penang y Malasia', 1786, 1957, M('Malaysia'), note='Establecimientos de los Estrechos y estados malayos protegidos'),
    E('Trinidad', 1797, 1962, M('Trinidad')),
    E('Malta', 1800, 1964, M('Malta')),
    E('Colonia del Cabo y Sudáfrica', 1795, 1931, M('South Africa'), note='Unión Sudafricana en 1910'),
    E('Sierra Leona', 1808, 1961, M('Sierra Leone')),
    E('Heligoland', 1807, 1890, P(7.89, 54.18), note='Canjeada con Alemania por Zanzíbar'),
    E('Buenos Aires', 1806, 1807, P(-58.38, -34.6), 'occupation', 'Invasiones inglesas del Río de la Plata'),
    E('Mauricio', 1810, 1968, P(57.55, -20.2)),
    E('Seychelles', 1814, 1976, P(55.45, -4.6)),
    E('Guayana Británica', 1814, 1966, M('Guyana')),
    E('Islas Jónicas', 1815, 1864, P(19.9, 39.6), 'dependent', 'Protectorado; cedidas a Grecia'),
    E('Gambia', 1816, 1965, M('Gambia, The')),
    E('Singapur', 1819, 1963, P(103.82, 1.35)),
    E('Costa de Oro', 1821, 1957, D(M('Ghana'), I(M('Ghana'), H(1914,'Togoland'))), note='Contorno acumulado aproximado; excluye el futuro Togoland británico'),
    E('Birmania', 1824, 1948, M('Burma'), note='Conquistada en tres guerras (1824–1885)'),
    E('Malvinas', 1833, None, P(-59.5, -51.7), note='Soberanía disputada por Argentina'),
    E('Adén y protectorado', 1839, 1967, M('Yemen', clip=(43, 12.4, 54, 16.8))),
    E('Nueva Zelanda', 1840, 1907, M('New Zealand')),
    E('Hong Kong', 1841, 1997, M('Hong Kong')),
    E('Basutolandia', 1868, 1966, M('Lesotho')),
    E('Lagos y Nigeria', 1861, 1960, M('Nigeria')),
    E('Fiyi', 1874, 1970, M('Fiji')),
    E('Chipre', 1878, 1960, M('Cyprus', 'Turkish Cypriot-administered area')),
    E('Afganistán · protectorado', 1879, 1919, M('Afghanistan'), 'influence', 'Política exterior bajo control británico'),
    E('Egipto', 1882, 1922, M('Egypt'), 'dependent', 'Ocupación y protectorado; influencia hasta 1956'),
    E('Somalilandia', 1884, 1960, M('Somalia', clip=(42.6, 8, 51.5, 11.5))),
    E('Papúa británica · Port Moresby', 1884, 1906, P(147.18,-9.48), 'dependent', 'Protectorado del sureste de Nueva Guinea; punto localizador sin extenderlo al norte alemán; administración australiana desde 1906'),
    E('Bechuanalandia', 1885, 1966, M('Botswana')),
    E('Rodesia', 1888, 1980, M('Zimbabwe', 'Zambia'), note='Compañía Británica de Sudáfrica; Rhodesia del Norte hasta 1964'),
    E('Brunéi', 1888, 1984, M('Brunei'), 'dependent', 'Protectorado'),
    E('Niasalandia', 1891, 1964, M('Malawi')),
    E('Uganda', 1894, 1962, M('Uganda')),
    E('África Oriental Británica', 1895, 1963, M('Kenya')),
    E('Weihaiwei', 1898, 1930, P(122.1, 37.5), note='Arrendamiento en China'),
    E('Sudán angloegipcio', 1899, 1956, M('Sudan'), 'dependent', 'Condominio con Egipto'),
    E('Kuwait', 1899, 1961, M('Kuwait'), 'dependent', 'Protectorado'),
    E('Estados de la Tregua', 1820, 1971, M('United Arab Emirates'), 'dependent', 'Tratados de tregua y protectorado'),
    E('Baréin', 1861, 1971, P(50.55, 26.07), 'dependent', 'Protectorado'),
    E('Catar', 1916, 1971, M('Qatar'), 'dependent', 'Protectorado'),
    E('Omán', 1891, 1971, M('Oman'), 'influence', 'Tratados de protección y tutela informal'),
    E('Suazilandia', 1903, 1968, M('Swaziland')),
    E('Tonga', 1900, 1970, M('Tonga'), 'dependent', 'Protectorado'),
    E('Tanganica', 1919, 1961, M('Tanzania, United Republic of'), note='Mandato de la Sociedad de Naciones; con Zanzíbar (1890–1963)'),
    E('Camerún británico', 1916, 1961, M('Cameroon', clip=(8.4, 4, 11.2, 10.8)), note='Franja occidental; contorno aproximado'),
    E('Palestina', 1920, 1948, M('Israel'), 'dependent', 'Mandato'),
    E('Transjordania', 1921, 1946, M('Jordan'), 'dependent', 'Mandato'),
    E('Irak', 1920, 1932, M('Iraq'), 'dependent', 'Mandato'),
    E('Islandia', 1940, 1941, M('Iceland'), 'occupation', 'Ocupación aliada preventiva'),
    E('Libia', 1943, 1951, M('Libya', clip=(9, 22, 25.2, 33.5)), 'occupation', 'Administración militar de Tripolitania y Cirenaica'),
    E('Eritrea', 1941, 1952, M('Eritrea'), 'occupation', 'Administración militar'),
    E('Zona británica de Alemania', 1945, 1949, M('Germany', clip=(5.8, 50.3, 11.3, 55)), 'occupation', 'Zona de ocupación aliada (aproximada)'),
    E('Islas Salomón', 1893, 1978, P(160, -9.5)),
    E('Islas Gilbert', 1892, 1979, P(173, 1.4)),
    E('Maldivas', 1887, 1965, P(73.5, 4.2), 'dependent', 'Protectorado'),
]
GB_CUTS = [(1650, 'Las primeras colonias', 'Irlanda, Virginia, Nueva Inglaterra y las islas del azúcar.'),
           (1763, 'Tras la guerra de los Siete Años', 'Canadá, Florida y Bengala; el primer imperio en su cénit.'),
           (1815, 'Después de Napoleón', 'Perdidas las Trece Colonias, Australia, el Cabo y Ceilán.'),
           (1880, 'El imperio victoriano', 'La India de la Corona, Nueva Zelanda, Hong Kong.'),
           (1921, 'La mayor extensión', 'El reparto de África y los mandatos de Oriente Medio.'),
           (1997, 'Todos los territorios', 'Acumulado completo hasta la entrega de Hong Kong.')]
GB_PER = [(1650, 'Hasta 1650', C6[0]), (1763, '1651–1763', C6[1]), (1815, '1764–1815', C6[2]),
          (1880, '1816–1880', C6[3]), (1913, '1881–1913', C6[4]), (9999, 'Desde 1914', C6[5])]
britain = dict(id='max-britanico', title='Todo lo que fue británico', subtitle='El imperio donde no se ponía el sol', era='1541 – 1997',
    region='Mundo', divergence=1541, color='#c8574b', center=[15, 20], zoom=2, world=True, bounds=[[-50, -140], [70, 180]],
    tags=['Imperio británico', 'Extensión acumulada'],
    summary='Todo territorio gobernado, protegido u ocupado alguna vez por Inglaterra y el Reino Unido: de las Trece Colonias a Hong Kong, pasando por los mandatos y las ocupaciones de las guerras mundiales.',
    limits='Mapa acumulado. Contornos modernos o generalizados. Protectorados, mandatos y esferas de influencia se separan del dominio directo; muchos dominios fueron autónomos mucho antes de su independencia formal.',
    sources=[HBSRC, src('The National Archives · imperio británico', 'https://www.nationalarchives.gov.uk/education/empire/'),
             src('Proclamación Real de 1763 · Avalon Project', 'https://avalon.law.yale.edu/18th_century/proc1763.asp')],
    entries=BRIT, cuts=GB_CUTS, periods=GB_PER)

# ══ 5. Imperio francés ════════════════════════════════════════════════════════
FRA = [
    E('Francia', 1534, None, M('France'), note='Núcleo metropolitano'),
    E('Nueva Francia · Canadá y Acadia', 1608, 1763, M('Canada', clip=(-80, 44, -59, 52)), note='Valle del San Lorenzo; cedida a Gran Bretaña'),
    E('Placentia', 1662, 1713, P(-53.97, 47.24), 'influence', 'Plaza de Terranova'),
    E('Luisiana francesa', 1682, 1763, H(1715, 'Louisiana'), 'claim', 'Inmensa reclamación del Misisipi con pocos puestos; vendida en 1803 tras recuperarla'),
    E('Nueva Orleans', 1718, 1803, P(-90.07, 29.95)),
    E('San Pedro y Miquelón', 1763, None, P(-56.2, 46.8)),
    E('Martinica y Guadalupe', 1635, None, M('Martinique', 'Guadeloupe')),
    E('Antillas disputadas', 1650, 1814, M('Saint Lucia', 'Dominica', 'Grenada', 'Saint Martin', 'Saint Barthelemy'), note='Soberanía alterna con Gran Bretaña'),
    E('Guayana Francesa', 1664, None, M('French Guiana')),
    E('Saint-Domingue', 1697, 1804, M('Haiti'), note='La colonia más rica; independiente como Haití'),
    E('Santo Domingo', 1795, 1809, M('Dominican Republic'), 'occupation', 'Cedido por España en Basilea'),
    E('Francia Antártica', 1555, 1567, P(-43.17, -22.9), 'influence', 'Colonia hugonote en la bahía de Guanabara'),
    E('Francia Equinoccial', 1612, 1615, P(-44.3, -2.53), 'influence', 'Fundación de São Luís'),
    E('San Luis de Senegal y Gorea', 1659, 1960, M('Senegal'), note='Factorías costeras; conquista del interior desde 1850'),
    E('Fort-Dauphin', 1643, 1674, P(46.98, -25.03), 'influence', 'Primer establecimiento en Madagascar'),
    E('Isla Borbón · Reunión', 1665, None, P(55.53, -21.1)),
    E('Isla de Francia · Mauricio', 1715, 1810, P(57.55, -20.2), note='Conquistada por los británicos'),
    E('Seychelles', 1756, 1810, P(55.45, -4.6)),
    E('Pondichery y factorías de la India', 1674, 1954, U(P(79.83, 11.93), P(88.37, 22.87), P(79.83, 10.92), P(75.53, 11.7), P(82.2, 16.73)), note='Pondichery, Chandernagor, Karikal, Mahé y Yanaon'),
    E('Decán y Carnático · esfera de Dupleix', 1749, 1761, M('India', clip=(76, 10, 82, 19.5)), 'influence', 'Nababes aliados; perdida en la guerra de los Siete Años'),
    E('Egipto', 1798, 1801, M('Egypt'), 'occupation', 'Campaña de Bonaparte'),
    E('Bélgica', 1795, 1814, M('Belgium', 'Luxembourg'), note='Anexionada a la República'),
    E('Orilla izquierda del Rin', 1797, 1814, M('Germany', clip=(6, 49.1, 8.3, 51.9)), note='Departamentos renanos'),
    E('Países Bajos', 1810, 1813, M('Netherlands'), note='Anexionados al Imperio'),
    E('Departamentos hanseáticos', 1810, 1814, M('Germany', clip=(6.6, 52, 11, 54.4)), note='Hamburgo, Bremen y Lübeck'),
    E('Italia napoleónica', 1796, 1814, M('Italy'), 'dependent', 'Piamonte, Toscana y Roma anexionados; Reino de Italia y Nápoles satélites'),
    E('Provincias Ilirias', 1809, 1814, M('Slovenia', 'Croatia'), note='Anexionadas al Imperio'),
    E('Confederación del Rin', 1806, 1813, M('Germany'), 'influence', 'Estados alemanes bajo protectorado de Napoleón'),
    E('Ducado de Varsovia', 1807, 1813, M('Poland'), 'dependent', 'Estado satélite'),
    E('España', 1808, 1814, M('Spain'), 'occupation', 'Guerra de la Independencia; Cataluña anexionada en 1812'),
    E('Campaña de Rusia', 1812, 1812, U(M('Lithuania', 'Byelarus'), M('Russia', clip=(27, 53.5, 38, 56.5))), 'occupation', 'Hasta Moscú y vuelta'),
    E('Argelia', 1830, 1962, M('Algeria'), note='Integrada en la Francia metropolitana desde 1848'),
    E('Gabón', 1839, 1960, M('Gabon')),
    E('Comoras y Mayotte', 1841, 1975, P(43.3, -11.7), note='Mayotte sigue siendo francesa'),
    E('Nueva Caledonia', 1853, None, P(165.6, -21.3)),
    E('Polinesia Francesa', 1842, None, P(-149.4, -17.65)),
    E('Wallis y Futuna', 1888, None, M('Wallis and Futuna Islands')),
    E('Indochina', 1858, 1954, M('Vietnam', 'Laos', 'Cambodia'), note='Cochinchina (1862), Camboya, Annam, Tonkín y Laos'),
    E('Segundo Imperio mexicano', 1862, 1867, M('Mexico'), 'occupation', 'Intervención y monarquía de Maximiliano'),
    E('Yibuti', 1862, 1977, M('Djibouti')),
    E('Túnez', 1881, 1956, M('Tunisia'), 'dependent', 'Protectorado'),
    E('África Occidental Francesa', 1880, 1960, M('Mauritania', 'Mali', 'Guinea', 'Ivory Coast', 'Burkina Faso', 'Niger', 'Benin'), note='Conquista del interior entre 1880 y 1900'),
    E('África Ecuatorial Francesa', 1880, 1960, M('Congo', 'Central African Republic', 'Chad'), note='Expediciones de Brazza'),
    E('Madagascar', 1896, 1960, M('Madagascar')),
    E('Guangzhouwan', 1898, 1945, P(110.4, 21.2), note='Territorio arrendado en China'),
    E('Marruecos', 1912, 1956, M('Morocco'), 'dependent', 'Protectorado (sin la zona española)'),
    E('Togo', 1916, 1960, M('Togo'), note='Mandato'),
    E('Camerún', 1916, 1960, M('Cameroon'), note='Mandato'),
    E('Siria y Líbano', 1920, 1946, M('Syria', 'Lebanon'), 'dependent', 'Mandato'),
    E('Nuevas Hébridas', 1906, 1980, P(167.5, -16), 'dependent', 'Condominio franco-británico'),
    E('Fezán', 1943, 1951, M('Libya', clip=(9, 22, 17, 30)), 'occupation', 'Administración militar'),
    E('Zona francesa de Alemania', 1945, 1949, M('Germany', clip=(6, 47.5, 10.2, 50.2)), 'occupation', 'Zona de ocupación aliada (aproximada)'),
]
FR_CUTS = [(1700, 'El primer imperio colonial', 'Nueva Francia, las Antillas, Senegal y las factorías del Índico.'),
           (1763, 'La gran pérdida', 'Canadá y la India pasan a Gran Bretaña tras la guerra de los Siete Años.'),
           (1812, 'El Gran Imperio', 'Napoleón anexiona Bélgica, Holanda y medio Italia, y domina el continente.'),
           (1880, 'El segundo imperio colonial', 'Argelia, Indochina y la aventura mexicana.'),
           (1920, 'Mandatos y protectorados', 'El reparto de África y los mandatos de Siria y el Líbano.'),
           (1980, 'Todos los territorios', 'Acumulado completo, con los territorios de ultramar que siguen siendo franceses.')]
FR_PER = [(1788, 'Antiguo Régimen', C6[0]), (1815, 'Revolución e Imperio', C6[2]), (1879, '1816–1879', C6[3]),
          (1913, '1880–1913', C6[4]), (9999, 'Desde 1914', C6[5])]
france = dict(id='max-frances', title='Todo lo que fue francés', subtitle='Dos imperios coloniales y uno continental', era='1534 – 1980',
    region='Mundo', divergence=1534, color='#5b8cff', center=[15, 0], zoom=2, world=True, bounds=[[-45, -130], [62, 170]],
    tags=['Imperio francés', 'Napoleón', 'Extensión acumulada'],
    summary='Nueva Francia y Luisiana, la Europa napoleónica, el gran imperio africano y asiático de la Tercera República: todo lo que Francia gobernó, protegió u ocupó alguna vez.',
    limits='Mapa acumulado. La Luisiana y buena parte de Nueva Francia fueron reclamaciones con escasos puestos. Las anexiones napoleónicas se aproximan con fronteras modernas.',
    sources=[HBSRC, src('Archives nationales d’outre-mer', 'https://recherche-anom.culture.gouv.fr/'),
             src('Fondation Napoléon · el Gran Imperio', 'https://www.napoleon.org/')],
    entries=FRA, cuts=FR_CUTS, periods=FR_PER)

# ══ 6. Roma ═══════════════════════════════════════════════════════════════════
R = 'roma'
ROME = [
    E('Italia', -264, 476, D(M('Italy'), U(M('Italy', clip=(8, 36.5, 15.7, 38.25)), M('Italy', clip=(8, 38.8, 10, 41.3)))), within=R, note='Península unificada bajo Roma tras la guerra de Pirro'),
    E('Sicilia', -241, 476, M('Italy', clip=(12, 36.5, 15.7, 38.4)), within=R, note='Primera provincia, tras la primera guerra púnica'),
    E('Cerdeña y Córcega', -238, 476, U(M('Italy', clip=(8, 38.8, 10, 41.3)), M('France', clip=(8.5, 41.3, 9.6, 43.1))), within=R),
    E('Hispania', -218, 409, M('Spain', 'Portugal'), within=R, note='Conquista completada por Augusto en el 19 a. C.; el sureste vuelve a ser romano (bizantino) entre 552 y 624'),
    E('Iliria', -168, 476, M('Albania', 'Montenegro', 'Croatia', 'Bosnia and Herzegovina'), within=R),
    E('África proconsular', -146, 439, M('Tunisia'), within=R, note='Tras la destrucción de Cartago'),
    E('Macedonia y Acaya', -146, 1453, M('Greece', 'Macedonia'), within=R, note='Continúa bajo el Imperio de Oriente'),
    E('Asia', -133, 1453, M('Turkey', clip=(26, 36, 31, 42)), within=R, note='Legado de Pérgamo'),
    E('Galia Narbonense', -121, 476, M('France', clip=(-1, 42.3, 7.8, 45.3)), within=R),
    E('Cirenaica y Creta', -74, 642, M('Libya', clip=(18, 29, 25.5, 33.5)), within=R),
    E('Siria y Cilicia', -64, 636, M('Syria', 'Lebanon', 'Israel', 'Turkey', clip=(32, 29, 42.5, 37.8)), within=R, note='Conquista de Pompeyo'),
    E('Numidia y Tripolitania', -46, 439, M('Algeria', 'Libya', clip=(3, 29, 18, 37.5)), within=R),
    E('Galia', -50, 476, M('France', 'Belgium', 'Luxembourg', 'Switzerland', 'Netherlands', 'Germany', clip=(-5, 42, 9, 53)), within=R, note='Conquista de César'),
    E('Egipto', -30, 641, M('Egypt'), within=R, note='Tras Accio'),
    E('Galacia, Capadocia y Ponto', -25, 1453, M('Turkey'), within=R),
    E('Retia, Nórico y Panonia', -15, 476, M('Austria', 'Slovenia', 'Hungary', 'Switzerland', 'Germany', 'Serbia', clip=(8, 44, 22, 49)), within=R),
    E('Germania Magna', -12, 9, M('Germany', clip=(6.5, 50.3, 12.5, 54.5)), 'occupation', 'Hasta el desastre de Teutoburgo'),
    E('Mesia y Tracia', 6, 1453, M('Serbia', 'Bulgaria', 'Romania', clip=(19, 41, 30, 45)), within=R),
    E('Judea y Arabia', 6, 636, M('Israel', 'Jordan'), within=R, note='Arabia Pétrea anexionada por Trajano en 106'),
    E('Mauritania', 40, 429, M('Morocco', 'Algeria', clip=(-10, 30, 3.2, 37)), within=R),
    E('Britania', 43, 410, M('United Kingdom', clip=(-6, 49.8, 2, 55.1)), within=R, note='Hasta el muro de Adriano'),
    E('Escocia antonina', 142, 162, M('United Kingdom', clip=(-5.5, 55, -2, 56.1)), 'occupation', 'Muro de Antonino'),
    E('Bósforo cimerio', 63, 341, H(100, 'Bosporian Kingdom'), 'dependent', 'Reino cliente de Crimea'),
    E('Dacia', 106, 271, U(H(100, 'Dacia'), M('Romania', clip=(21, 44, 26, 48))), note='Conquista de Trajano; abandonada por Aureliano'),
    E('Armenia', 114, 117, M('Armenia', 'Azerbaijan', 'Georgia'), 'occupation', 'Provincia efímera de Trajano'),
    E('Mesopotamia y Asiria', 116, 117, M('Iraq', 'Kuwait'), 'occupation', 'Campaña pártica de Trajano'),
    E('Crimea bizantina', 527, 1475, M('Ukraine', clip=(32.5, 44.3, 36.7, 45.5)), 'influence', 'Quersoneso y Gotia'),
]
roma = dict(id='max-roma', title='Todo lo que fue romano', subtitle='De la Italia republicana a Justiniano', era='264 a. C. – 1453',
    region='Mediterráneo', divergence=-264, color='#c9a24a', center=[40, 15], zoom=3.5, world=False, bounds=[[22, -12], [58, 50]],
    extents={R: U(H(100, 'Roman Empire'), H(200, 'Roman Empire'), H(100, 'Dacia'))},
    tags=['Roma', 'Antigüedad', 'Extensión acumulada'],
    summary='Cada provincia que Roma gobernó alguna vez, con su fecha de anexión: de Sicilia en el 241 a. C. a las conquistas efímeras de Trajano en Mesopotamia y la Hispania bizantina de Justiniano.',
    limits='Provincias aproximadas recortando fronteras modernas con la extensión romana de los años 100–200. Las fechas de pérdida siguen al Imperio de Occidente (476) o, en Oriente, a 1453.',
    sources=[HBSRC, src('Atlas digital del Imperio romano (DARE)', 'https://imperium.ahlfeldt.se/'),
             src('Pleiades · gazetteer del mundo antiguo', 'https://pleiades.stoa.org/')],
    entries=ROME, periods=[(-134, 'República media', C6[0]), (-28, 'República tardía', C6[1]), (96, 'Augusto y los Julio-Claudios', C6[2]), (180, 'Trajano y los Antoninos', C6[3]), (9999, 'Imperio de Oriente', C6[5])],
    cuts=[(-201, 'Tras Aníbal', 'Italia, las islas y las primeras Hispanias.'),
          (-133, 'Señora del Mediterráneo', 'Cartago y Corinto destruidas; herencia de Pérgamo.'),
          (-27, 'Fin de la República', 'César conquista la Galia; Pompeyo, Oriente; Egipto tras Accio.'),
          (117, 'Máxima extensión', 'Trajano añade Dacia, Arabia, Armenia y Mesopotamia.'),
          (565, 'Justiniano', 'El Imperio de Oriente recupera África, Italia y el sureste de Hispania.'),
          (1453, 'Todos los territorios', 'Acumulado completo de Roma.')])

# ══ 7. Mongoles ═══════════════════════════════════════════════════════════════
MG = 'mongol'
MONG = [
    E('Mongolia de Gengis Kan', 1206, 1368, H(1200, 'Mongol Empire'), note='Unificación de las tribus en 1206'),
    E('Xi Xia', 1227, 1368, M('China', clip=(97, 35, 110, 42.5)), within=MG, note='Reino tangut destruido en 1227'),
    E('Kara Khitai y Asia central', 1218, 1368, M('Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'China', clip=(68, 35, 97, 50)), within=MG),
    E('Corasmia', 1221, 1335, M('Uzbekistan', 'Turkmenistan', 'Afghanistan'), within=MG),
    E('China del norte · Jin', 1234, 1368, M('China', clip=(105, 32, 126, 45)), within=MG),
    E('Rus de Kiev y estepa', 1240, 1480, M('Russia', 'Ukraine', 'Byelarus', 'Moldova', clip=(22, 44, 60, 60)), within=MG, note='Principados rusos tributarios de la Horda de Oro hasta 1480'),
    E('Novgorod y Riazán', 1240, 1480, U(H(1279, 'Novgorod'), H(1279, 'Ryazan')), 'dependent', 'Principados tributarios'),
    E('Siberia occidental y Urales', 1237, 1480, M('Russia', 'Kazakhstan', clip=(45, 48, 90, 62)), within=MG, note='Horda Blanca y Horda de Oro'),
    E('Georgia y Armenia', 1236, 1335, M('Georgia', 'Armenia', 'Azerbaijan'), 'dependent', 'Reinos vasallos'),
    E('Sultanato de Rum', 1243, 1308, M('Turkey', clip=(29, 36, 44, 42)), 'dependent', 'Selyúcidas vasallos tras Köse Dağ'),
    E('Hungría', 1241, 1242, M('Hungary'), 'occupation', 'Invasión de Batu y Subotai'),
    E('Polonia meridional', 1241, 1241, M('Poland', clip=(15, 49, 23, 51.5)), 'occupation', 'Batalla de Legnica'),
    E('Bulgaria', 1242, 1300, M('Bulgaria'), 'dependent', 'Tributaria de la Horda de Oro'),
    E('Persia e Irak', 1256, 1335, M('Iran', 'Iraq'), within=MG, note='Ilkanato; caída de Bagdad en 1258'),
    E('Tíbet', 1247, 1354, M('China', clip=(78, 27, 99, 37)), 'dependent', 'Bajo la protección de los Sakya y la dinastía Yuan'),
    E('Dali · Yunnan', 1253, 1368, M('China', clip=(97, 21, 106, 29)), note='Conquistado por Möngke y Kublai'),
    E('Corea · Goryeo', 1259, 1356, M("Korea, Republic of", "Korea, Democratic People's Republic of"), 'dependent', 'Reino vasallo'),
    E('Siria', 1260, 1300, M('Syria'), 'occupation', 'Ocupaciones de 1260 y 1299–1300'),
    E('Sajalín', 1264, 1308, M('Russia', clip=(141.5, 45.9, 144.8, 54.5)), 'influence', 'Campañas contra los ainu'),
    E('China del sur · Song', 1279, 1368, M('China', clip=(103, 18, 123, 32.1)), note='Dinastía Yuan de Kublai Kan'),
    E('Manchuria', 1234, 1368, M('China', 'Russia', clip=(119, 40, 135, 53)), within=MG),
    E('Dai Viet', 1258, 1288, M('Vietnam', clip=(102, 18, 109, 23.4)), 'occupation', 'Tres invasiones rechazadas'),
    E('Champa', 1283, 1285, P(108.9, 13.8), 'occupation', 'Expedición naval'),
    E('Birmania · Pagan', 1287, 1303, M('Burma', clip=(94, 20, 99, 26)), 'occupation', 'Invasión y protectorado'),
    E('Tsushima, Iki y Hakata', 1274, 1281, U(P(129.3, 34.4), P(130.4, 33.6)), 'occupation', 'Invasiones de Japón, frustradas por los tifones'),
    E('Java', 1293, 1293, P(112.7, -7.5), 'occupation', 'Expedición contra Singhasari'),
    E('Punyab', 1299, 1303, M('Pakistan', clip=(69, 29, 75, 34)), 'occupation', 'Incursiones del kanato de Chagatai'),
]
mongols = dict(id='max-mongol', title='Todo lo que fue mongol', subtitle='Gengis Kan y los kanatos sucesores', era='1206 – 1480',
    region='Eurasia', divergence=1206, color='#d78a3c', center=[44, 80], zoom=3, world=True, bounds=[[5, 10], [62, 150]],
    extents={MG: U(S(1279, 'Mongol Empire'), S(1300, 'Mongol Empire'), H(1300, 'Ilkhanate'))},
    tags=['Mongoles', 'Kanatos', 'Extensión acumulada'],
    summary='La mayor continuidad terrestre de la historia, sumando el imperio unificado y sus cuatro kanatos: de Hungría y Siria a Corea, y las expediciones a Japón, Vietnam y Java.',
    limits='Mapa acumulado a partir de las capas de 1200, 1279 y 1300, recortadas con fronteras modernas para fechar las conquistas. Las campañas fallidas y los tributarios se distinguen del dominio directo.',
    sources=[HBSRC, src('Imperio mongol · Encyclopaedia Iranica', 'https://www.iranicaonline.org/articles/mongols'),
             src('The Mongols in World History · Columbia University', 'https://afe.easia.columbia.edu/mongols/')],
    entries=MONG, periods=[(1227, 'Gengis Kan', C6[0]), (1259, 'Ögodei y Möngke', C6[1]), (1294, 'Kublai Kan', C6[2]), (9999, 'Kanatos sucesores', C6[3])],
    cuts=[(1206, 'Un pueblo unificado', 'Temujín es proclamado Gengis Kan.'),
          (1227, 'La muerte de Gengis', 'Xi Xia, Kara Khitai y el imperio de Corasmia.'),
          (1242, 'Hacia Europa', 'La Rus de Kiev, Polonia y Hungría.'),
          (1260, 'Bagdad y Siria', 'El Ilkanato destruye el califato; la ruptura del imperio.'),
          (1294, 'El imperio de Kublai', 'La China Song, Corea y las expediciones navales.'),
          (1480, 'Todos los territorios', 'Acumulado completo, hasta el fin del yugo tártaro sobre Moscú.')])

# ══ 8. Otomanos (método automático por capas + añadidos) ══════════════════════
OT_YEARS = [1400, 1492, 1530, 1600, 1650, 1700, 1715, 1783, 1800, 1815, 1880, 1900, 1914]
OT_VASSALS = ['Crimean Khanate', 'Algiers', 'Tunis', 'Tripolitania', 'Cyrenaica', 'Egypt', 'Harer \\(Egypt\\)']
def ottoman_entries():
    countries = [(p['NAME'], g) for p, g in hb(1994) if p.get('NAME')]
    es = {'Turkey': 'Anatolia', 'Greece': 'Grecia', 'Bulgaria': 'Bulgaria', 'Serbia': 'Serbia', 'Bosnia and Herzegovina': 'Bosnia', 'Albania': 'Albania', 'Macedonia': 'Macedonia', 'Montenegro': 'Montenegro', 'Croatia': 'Eslavonia', 'Hungary': 'Hungría', 'Romania': 'Rumanía', 'Moldova': 'Besarabia', 'Ukraine': 'Crimea y el Ponto', 'Russia': 'Costa del mar Negro', 'Georgia': 'Georgia', 'Armenia': 'Armenia', 'Azerbaijan': 'Azerbaiyán', 'Iran': 'Persia occidental', 'Iraq': 'Irak', 'Syria': 'Siria', 'Lebanon': 'Líbano', 'Israel': 'Palestina', 'Jordan': 'Transjordania', 'Saudi Arabia': 'Hiyaz y Lahsa', 'Yemen': 'Yemen', 'Egypt': 'Egipto', 'Libya': 'Libia', 'Tunisia': 'Túnez', 'Algeria': 'Argelia', 'Sudan': 'Sudán', 'Eritrea': 'Eritrea', 'Cyprus': 'Chipre', 'Turkish Cypriot-administered area': 'Chipre', 'Kuwait': 'Kuwait', 'Qatar': 'Catar', 'Slovakia': 'Alta Hungría', 'Ethiopia': 'Habesh', 'Somalia': 'Zeila', 'Djibouti': 'Zeila', 'Oman': 'Omán', 'United Arab Emirates': 'Golfo'}
    geoms = {}
    for y in OT_YEARS:
        pats = [re.compile('^Ottoman Empire$')] + [re.compile('^' + v + '$') for v in OT_VASSALS]
        g = unary_union([gg for p, gg in hb(y) if any(r.match(str(p.get('SUBJECTO') or '')) or r.match(str(p.get('NAME') or '')) for r in pats)])
        geoms[y] = make_valid(g).buffer(0)
    acc = None; out = []
    for y in OT_YEARS:
        new = geoms[y] if acc is None else geoms[y].difference(acc)
        acc = geoms[y] if acc is None else unary_union([acc, geoms[y]])
        for n, cg in countries:
            piece = new.intersection(cg)
            if piece.is_empty or piece.area < .25: continue
            seen = [yy for yy in OT_YEARS if yy >= y and geoms[yy].intersection(piece).area > .5 * piece.area]
            last = seen[-1] if seen else y
            end = None if last == 1914 and n == 'Turkey' else (1922 if last == 1914 else last)
            vas = n in ('Egypt', 'Tunisia', 'Algeria', 'Libya', 'Sudan', 'Ukraine', 'Russia', 'Romania', 'Moldova')
            out.append(E(es.get(n, n), y, end, ('geom', piece), 'dependent' if vas else 'sovereign',
                         f'Primera aparición en la capa de {y}; presente hasta la de {last}' + (' (vasallos o autonomía amplia)' if vas else '')))
    return out
OTTO_EXTRA = [
    E('Valaquia', 1417, 1878, M('Romania', clip=(22.3, 43.6, 28, 45.3)), 'dependent', 'Principado tributario'),
    E('Moldavia', 1456, 1878, U(M('Romania', clip=(26, 45.3, 30, 48.3)), M('Moldova')), 'dependent', 'Principado tributario'),
    E('Transilvania', 1570, 1699, M('Romania', clip=(21, 45.3, 26, 48)), 'dependent', 'Principado vasallo'),
    E('Otranto', 1480, 1481, P(18.49, 40.15), 'occupation', 'Desembarco en Italia'),
    E('Podolia', 1672, 1699, M('Ukraine', clip=(26, 48, 30, 50)), note='Eyalato de Kamaniçe'),
    E('Ragusa', 1458, 1806, P(18.1, 42.64), 'dependent', 'República tributaria'),
    E('Aceh', 1565, 1570, P(95.32, 5.55), 'influence', 'Expedición naval de apoyo al sultanato'),
    E('Massaua y Habesh', 1557, 1872, P(39.45, 15.6), note='Eyalato del mar Rojo'),
]
def resolve_geom(spec):  # extensión para piezas precalculadas
    return spec[1]
_orig_resolve = resolve
def resolve(spec):  # noqa: F811
    return spec[1] if spec[0] == 'geom' else _orig_resolve(spec)
otto = dict(id='max-otomano', title='Todo lo que fue otomano', subtitle='Seis siglos entre Viena, Argel y Basora', era='1400 – 1922',
    region='Mediterráneo · Oriente Medio', divergence=1400, color='#3aa58f', center=[36, 30], zoom=3.5, world=False, bounds=[[10, -5], [52, 55]],
    tags=['Imperio otomano', 'Extensión acumulada'],
    summary='Todos los territorios que gobernó o tuvo como vasallos la dinastía de Osmán: Hungría y Podolia, las regencias berberiscas, Egipto, el Hiyaz y el Yemen. Fechado automáticamente con trece cortes cartográficos.',
    limits='Fechas aproximadas: cada región se data por su primera aparición en las capas disponibles (1400, 1492, 1530…), no por la fecha exacta de conquista. Se añaden a mano principados tributarios y campañas breves.',
    sources=[HBSRC, src('Imperio otomano · Encyclopaedia Britannica', 'https://www.britannica.com/place/Ottoman-Empire'),
             src('Ottoman Archives (Devlet Arşivleri)', 'https://www.devletarsivleri.gov.tr/')],
    entries=None, periods=[(1453, 'Hasta Constantinopla', C6[0]), (1530, 'Selim y Solimán', C6[1]), (1650, 'Siglos XVI–XVII', C6[2]), (1800, 'Siglo XVIII', C6[3]), (9999, 'Siglo XIX', C6[4])],
    cuts=[(1453, 'Constantinopla', 'Anatolia y los Balcanes antes de la caída de Bizancio.'),
          (1530, 'Solimán el Magnífico', 'Egipto, Siria, el Hiyaz y Hungría.'),
          (1683, 'Ante Viena', 'Creta, Podolia y la máxima extensión europea.'),
          (1800, 'Primeras pérdidas', 'Hungría y Crimea se pierden; Egipto, ocupado por Napoleón.'),
          (1914, 'El final', 'Los Balcanes independientes; Libia, perdida en 1912.'),
          (1922, 'Todos los territorios', 'Acumulado completo hasta la abolición del sultanato.')])


# ══ Nuevos escenarios alternativos ════════════════════════════════════════════
def A(name, spec, color, role='sovereign', note='', certainty='scenario'):
    return dict(name=name, spec=spec, color=color, role=role, note=note, certainty=certainty)

def alt_build(cfg):
    cache = {}
    def feat(a):
        key = repr(a['spec'])
        if key not in cache:
            g = resolve(a['spec'])
            if g.geom_type not in ('Point', 'MultiPoint'): g = make_valid(g).buffer(0)
            cache[key] = simplify(g)
        return dict(type='Feature', geometry=cache[key], properties=dict(name=a['name'], color=a['color'], role=a['role'],
                    note=a['note'], certainty=a['certainty'], approx=True))
    frames = []
    for year, title, text, items, historical in cfg['frames']:
        fs = [feat(a) for a in items]
        if historical:
            for f in fs: f['properties']['certainty'] = 'documented'
        frames.append(dict(year=year, title=title, text=text, features=fs, historical=historical))
    sc = {k: v for k, v in cfg.items() if k != 'frames'}
    sc['frames'] = frames
    for fr in frames:
        for f in fr['features']:
            p = f['properties']
            p['id'] = sc['id'] + '-' + hashlib.sha256((p['name'] + json.dumps(f['geometry'])[:200]).encode()).hexdigest()[:12]
            p['validAt'] = fr['year']
            p['representation'] = 'area'
    print(f"{sc['id']}: {len(frames)} etapas")
    return sc

GREY = '#3d4555'

# ── México conserva el norte ──
TEXAS = U(M('United States', clip=(-106.6, 25.8, -93.6, 34.0)), M('United States', clip=(-103.05, 34.0, -100.0, 36.5)))
NORTE = D(M('United States', clip=(-124.8, 31.3, -102.0, 42.0)), TEXAS)
USA = D(M('United States', clip=(-125, 24, -66, 49.5)), U(TEXAS, NORTE))
CAM = M('Guatemala', 'El Salvador', 'Honduras', 'Nicaragua', 'Costa Rica')
mx_core = A('México', M('Mexico'), '#3fae7a', note='Estados del centro y sur de la República.')
mx_us = A('Estados Unidos', USA, GREY, note='Referencia: contorno aproximado de Estados Unidos al este del límite de 1819.', certainty='documented')
mx_tx = lambda role, note: A('Texas', TEXAS, '#9ccf7a', role, note)
mx_no = lambda role, note: A('Alta California y Nuevo México', NORTE, '#c9d86a', role, note)
mexico = dict(id='mexico-norte', title='México conserva su norte', subtitle='Sin guerra de 1846 ni secesión texana', era='Siglo XIX',
    region='Norteamérica', divergence=1836, color='#3fae7a', center=[30, -102], zoom=4, world=True, bounds=[[12, -126], [45, -82]],
    tags=['México', 'Texas', 'California'],
    summary='Un pacto federal con los colonos de Texas evita la secesión de 1836 y, sin la anexión texana, no estalla la guerra de 1846. México conserva el límite de 1819 y la fiebre del oro californiana ocurre bajo bandera mexicana.',
    limits='Los límites del norte siguen aproximadamente el Tratado Adams-Onís (1819) recortado sobre fronteras modernas. Gran parte del septentrión seguía controlado por pueblos indígenas (comanches, apaches, navajos), lo que el mapa no resuelve.',
    sources=[src('Tratado Adams-Onís (1819) · Avalon Project', 'https://avalon.law.yale.edu/19th_century/sp1819.asp'),
             src('Tratado de Guadalupe Hidalgo (1848) · Avalon Project', 'https://avalon.law.yale.edu/19th_century/guadhida.asp'),
             src('Revolución de Texas · Texas State Historical Association', 'https://www.tshaonline.org/handbook/entries/texas-revolution')],
    frames=[(1822, 'El Imperio mexicano', 'Referencia: México independiente hereda el límite de 1819 y anexiona brevemente Centroamérica (1822–1823).',
             [mx_core, mx_tx('sovereign', 'Parte del estado de Coahuila y Texas; colonización angloamericana desde 1821.'),
              mx_no('claim', 'Septentrión con misiones, presidios y ranchos dispersos; amplias zonas bajo control indígena.'),
              A('Centroamérica', CAM, '#b6a36a', 'dependent', 'Unida al Imperio de Iturbide en 1822; se separa en 1823.'), mx_us], True),
            (1836, 'Un pacto con Texas', 'Divergencia: en lugar del centralismo de Santa Anna, una ley federal reconoce Texas como estado propio. No hay secesión.',
             [mx_core, mx_tx('federal', 'Estado federado con autonomía fiscal y garantías a los colonos. Hipótesis del escenario.'),
              mx_no('claim', 'Sin cambios: presencia mexicana dispersa.'), mx_us], False),
            (1848, 'Sin guerra con Estados Unidos', 'Sin anexión de Texas no hay casus belli. El oro de California (1848) atrae colonos a territorio mexicano.',
             [mx_core, mx_tx('federal', 'Estado federado de la República.'),
              mx_no('federal', 'Alta California y Nuevo México se organizan como estados ante la llegada de población.'), mx_us], False),
            (1880, 'Una república continental', 'Hipótesis: el ferrocarril une Ciudad de México con Santa Fe y San Francisco. Las tensiones con los colonos siguen abiertas.',
             [mx_core, mx_tx('federal', 'Estado federado de la República.'),
              mx_no('federal', 'Estados de California, Arizona, Nuevo México y Utah.'), mx_us], False)],
    ports=[dict(name=n, lon=x, lat=y, cat='port', start=s, note=t) for n, x, y, s, t in [
        ('Ciudad de México', -99.13, 19.43, 1822, 'Capital de la República.'), ('San Antonio de Béxar', -98.49, 29.42, 1822, 'Centro político de Texas.'),
        ('Santa Fe', -105.94, 35.69, 1822, 'Capital de Nuevo México.'), ('Monterey', -121.89, 36.6, 1822, 'Capital de la Alta California.'),
        ('San Francisco', -122.42, 37.77, 1848, 'Puerto de la fiebre del oro bajo bandera mexicana.')]],
    routes=[dict(name='Ferrocarril central del norte', coordinates=[[-99.13, 19.43], [-102.3, 21.9], [-106.1, 28.6], [-106.5, 31.7], [-105.94, 35.69]], cat='port', start=1880),
            dict(name='Ferrocarril del Pacífico', coordinates=[[-106.5, 31.7], [-110.9, 32.2], [-114.6, 32.7], [-118.24, 34.05], [-121.89, 36.6], [-122.42, 37.77]], cat='port', start=1880)])

# ── Centroamérica unida ──
CA_ST = [('Guatemala', '#5b8cff'), ('El Salvador', '#2bb5a6'), ('Honduras', '#a06cff'), ('Nicaragua', '#e0569b'), ('Costa Rica', '#f0b44c')]
CA_ES = {'Guatemala': 'Guatemala', 'El Salvador': 'El Salvador', 'Honduras': 'Honduras', 'Nicaragua': 'Nicaragua', 'Costa Rica': 'Costa Rica'}
MOSQ = M('Nicaragua', 'Honduras', clip=(-84.3, 10.9, -83.1, 15.9))
ALTOS = M('Guatemala', clip=(-92.3, 14.5, -90.9, 15.9))
def ca_states(role, note, mosq_out=True, altos=False):
    out = []
    for n, c in CA_ST:
        g = M(n)
        if n == 'Guatemala' and altos: g = D(g, ALTOS)
        if mosq_out and n in ('Nicaragua', 'Honduras'): g = D(g, MOSQ)
        out.append(A('Estado de ' + CA_ES[n], g, c, role, note))
    if altos: out.append(A('Estado de Los Altos', ALTOS, '#7fb0ff', role, 'Sexto estado, reconocido en la reforma constitucional del escenario (Quetzaltenango).'))
    return out
belice = A('Belice británico', M('Belize'), GREY, 'claim', 'Asentamiento británico reclamado por Guatemala y la Federación.', 'documented')
mosq = A('Reino misquito', MOSQ, '#b77f69', 'dependent', 'Protectorado británico en la costa caribeña.', 'documented')
camerica = dict(id='centroamerica', title='Centroamérica unida', subtitle='La República Federal no se disuelve', era='Siglo XIX',
    region='Centroamérica', divergence=1838, color='#5b8cff', center=[13, -86], zoom=6, world=True, bounds=[[7.5, -93], [18.5, -82]],
    tags=['Federación', 'Morazán', 'Canal'],
    summary='Una reforma constitucional en 1838 reparte el poder entre los estados y reconoce a Los Altos como sexto miembro. La federación sobrevive, recupera la costa misquita y construye el canal interoceánico por Nicaragua.',
    limits='Estados aproximados con fronteras modernas; Los Altos y la Mosquitia se dibujan de forma esquemática. Chiapas y Panamá quedan fuera, como en la historia real.',
    sources=[src('República Federal de Centroamérica · Encyclopaedia Britannica', 'https://www.britannica.com/place/United-Provinces-of-Central-America'),
             src('Tratado Clayton-Bulwer (1850) · Avalon Project', 'https://avalon.law.yale.edu/19th_century/br1850.asp'),
             src('Proyecto de canal por Nicaragua · Office of the Historian', 'https://history.state.gov/milestones/1899-1913/panama-canal')],
    frames=[(1824, 'Las Provincias Unidas', 'Referencia: la Constitución de 1824 crea una federación de cinco estados con capital en Guatemala.',
             ca_states('federal', 'Estado de la República Federal de Centroamérica (1824).') + [mosq, belice], True),
            (1838, 'Reforma en lugar de ruptura', 'Divergencia: el Congreso pacta más autonomía fiscal para los estados. Los Altos se incorpora como sexto estado.',
             ca_states('federal', 'Estado federado con autonomía fiscal ampliada. Hipótesis del escenario.', altos=True) + [mosq, belice], False),
            (1860, 'La costa misquita, reintegrada', 'Una federación más fuerte negocia con Londres el fin del protectorado misquito.',
             ca_states('federal', 'Estado federado.', mosq_out=False, altos=True) + [belice], False),
            (1914, 'El canal de Nicaragua', 'Hipótesis: el canal interoceánico se abre por el río San Juan y el lago de Nicaragua, no por Panamá.',
             ca_states('federal', 'Estado federado.', mosq_out=False, altos=True) + [belice], False)],
    ports=[dict(name=n, lon=x, lat=y, cat='port', start=s, note=t) for n, x, y, s, t in [
        ('Guatemala', -90.51, 14.64, 1824, 'Primera capital federal.'), ('San Salvador', -89.19, 13.69, 1834, 'Capital federal desde 1834.'),
        ('Quetzaltenango', -91.52, 14.84, 1838, 'Capital del estado de Los Altos.'), ('Greytown', -83.7, 10.92, 1860, 'Puerto caribeño de la Mosquitia.'),
        ('San Juan del Sur', -85.87, 11.25, 1914, 'Salida del canal al Pacífico.')]],
    routes=[dict(name='Canal interoceánico de Nicaragua', coordinates=[[-83.7, 10.92], [-84.2, 10.95], [-84.78, 11.12], [-85.4, 11.35], [-85.83, 11.44], [-85.87, 11.25]], cat='port', start=1914)])

# ── Las Tres Naciones (Hadiach) ──
PLC = H(1650, 'Polish.Lithuanian Commonwealth')
LIT = U(M('Lithuania', 'Byelarus', 'Latvia'), M('Russia', clip=(26, 51.5, 36, 57.5)), M('Ukraine', clip=(23, 51.4, 33, 52.5)))
RUT = M('Ukraine', clip=(27.3, 47.5, 36, 52.4))
def plc(three, rut_note='Voivodatos de Kiev, Bratslav y Chernígov.'):
    if not three:
        return [A('Corona del Reino de Polonia', D(PLC, LIT), '#d0556c', 'federal', 'Una de las dos naciones de la Unión de Lublin (1569).'),
                A('Gran Ducado de Lituania', ('diff', PLC, D(PLC, LIT)), '#5b8cff', 'federal', 'Segunda nación de la Mancomunidad.')]
    return [A('Corona del Reino de Polonia', D(PLC, U(LIT, RUT)), '#d0556c', 'federal', 'Una de las tres naciones de la Mancomunidad.'),
            A('Gran Ducado de Lituania', ('diff', PLC, D(PLC, LIT)), '#5b8cff', 'federal', 'Una de las tres naciones de la Mancomunidad.'),
            A('Gran Ducado de Rutenia', ('diff', PLC, D(PLC, RUT)), '#f0b44c', 'federal', 'Tercera nación creada en Hadiach, con hetman, cancillería y ejército propios. ' + rut_note)]
moscovia = A('Zarato de Moscovia', D(H(1650, 'Tsardom of Muscovy'), PLC), GREY, note='Referencia: rival oriental de la Mancomunidad.', certainty='documented')
tres = dict(id='tres-naciones', title='La Mancomunidad de las Tres Naciones', subtitle='Polonia, Lituania y Rutenia, unidas en Hadiach', era='Edad Moderna',
    region='Europa oriental', divergence=1658, color='#f0b44c', center=[51, 27], zoom=4.5, world=True, bounds=[[44, 13], [60, 42]],
    tags=['Hadiach', 'Cosacos', 'Mancomunidad'],
    summary='El Tratado de Hadiach (1658) convierte a la Ucrania cosaca en un tercer miembro de la Mancomunidad polaco-lituana. En el escenario se ratifica y se cumple: no hay partición de Andrúsovo y Kiev permanece en la unión.',
    limits='Los límites del Gran Ducado de Rutenia se aproximan con fronteras modernas; el tratado solo nombraba los voivodatos de Kiev, Bratslav y Chernígov. Se usa la capa de 1650 para la Mancomunidad.',
    sources=[src('Tratado de Hadiach · Encyclopedia of Ukraine', 'https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CH%5CA%5CHadiachTreatyof1658.htm'),
             src('Tregua de Andrúsovo (1667) · Encyclopaedia Britannica', 'https://www.britannica.com/event/Truce-of-Andrusovo'),
             src('Unión de Lublin (1569) · Encyclopaedia Britannica', 'https://www.britannica.com/event/Union-of-Lublin')],
    frames=[(1650, 'Las dos naciones', 'Referencia: la Mancomunidad polaco-lituana antes de la gran revuelta cosaca de Jmelnytsky.',
             plc(False) + [moscovia], True),
            (1658, 'El Tratado de Hadiach', 'Divergencia: la Dieta ratifica el tratado y los cosacos lo aceptan. Nace el Gran Ducado de Rutenia.',
             plc(True) + [moscovia], False),
            (1667, 'Sin partición de Ucrania', 'En lugar de Andrúsovo, una paz con Moscú reconoce la orilla izquierda del Dniéper y Kiev a la Mancomunidad.',
             plc(True, 'Incluye la orilla izquierda del Dniéper y Kiev.') + [moscovia], False),
            (1700, 'Una unión de tres pueblos', 'Hipótesis: la Mancomunidad entra en el siglo XVIII con tres naciones y un ejército cosaco propio.',
             plc(True, 'Incluye la orilla izquierda del Dniéper y Kiev.') + [moscovia], False)],
    ports=[dict(name=n, lon=x, lat=y, cat='port', start=s, note=t) for n, x, y, s, t in [
        ('Varsovia', 21.01, 52.23, 1650, 'Sede del rey y de la Dieta común.'), ('Vilna', 25.28, 54.69, 1650, 'Capital del Gran Ducado de Lituania.'),
        ('Kiev', 30.52, 50.45, 1658, 'Capital del Gran Ducado de Rutenia.'), ('Chernígov', 31.29, 51.49, 1658, 'Voivodato rutenio.')]],
    routes=[])
ALT_SCENARIOS = [mexico, camerica, tres]

def conform(sc):
    """Ajusta los metadatos al contrato de build_data.py / audit_data.py de Codex."""
    urls = [x['url'] for x in sc['sources']]
    for fr in sc['frames']:
        fr['basis'] = 'historical-reference' if fr['historical'] else 'counterfactual-interpretation'
        fr['geometryPolicy'] = 'discrete-snapshot-no-interpolation'
        fr['geographyNote'] = sc['limits']
        for f in fr['features']:
            p = f['properties']
            p['historicalBasis'] = p.get('certainty') == 'documented'
            p['certainty'] = 'documented' if fr['historical'] else 'scenario'
            p['entityId'] = sc['id'] + '-' + hashlib.sha256(p['name'].encode('utf-8')).hexdigest()[:12]
            p.setdefault('sourceUrls', urls)
            pt = f['geometry']['type'] in ('Point', 'MultiPoint')
            p['representation'] = 'location-marker' if pt else 'area'
            if pt: p['approx'] = True
    return sc

def export():
    from extension_complementos import apply_review
    apply_review(globals())
    scens = [spain, portugal, iberia, britain, france, roma, mongols]
    print('Calculando otomanos…'); otto['entries'] = ottoman_entries() + OTTO_EXTRA; scens.append(otto)
    built = [conform(build(c)) for c in scens] + [conform(alt_build(c)) for c in ALT_SCENARIOS]
    for s in built:
        (OUT / (s['id'] + '.js')).write_text('window.ATLAS_REGISTER(' + json.dumps(s, ensure_ascii=False, separators=(',', ':')) + ');', encoding='utf-8')
        (OUT / (s['id'] + '.json')).write_text(json.dumps(s, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        last = s['frames'][-1]
        (OUT / (s['id'] + '.geojson')).write_text(json.dumps(dict(type='FeatureCollection', name=s['title'], metadata=dict(year=last['year'], limits=s['limits'], sources=s['sources']), features=last['features']), ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    cat = [{k: v for k, v in s.items() if k not in ('frames', 'ports', 'routes', 'roleNames')} | {'years': [f['year'] for f in s['frames']]} for s in built]
    (OUT / 'catalog-extension.json').write_text(json.dumps(cat, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (OUT / 'catalog-extension.js').write_text('window.ATLAS_CATALOG.push(...' + json.dumps(cat, ensure_ascii=False, separators=(',', ':')) + ');', encoding='utf-8')
    print('Mapas añadidos:', len(built))

if __name__ == '__main__':
    export()

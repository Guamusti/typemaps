"""Shared plumbing for the ported v1 generators (task 2.3).

The ports keep the original code and only change where inputs are read from
(frozen originals and hash-verified HB layers) and how output geometry is written:
- ATLAS_TOLERANCE=.018 reproduces v1 exactly (make_valid + buffer(0) + simplify), for the equivalence test.
- ATLAS_TOLERANCE unset/none is the atlas mode: no simplification, make_valid only if invalid.
"""
import os, sys, json, hashlib
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[2]
BASES = ATLAS / 'source-data/bases'
ORIG = ATLAS / 'source-data/originales'
# Shapely is not vendored in the site; reuse the local copy the original maps already used.
LIBS = os.environ.get('ATLAS_SHAPELY_LIBS', str(ATLAS.parents[1] / 'mapas/potencias-centrales/.libs'))
if Path(LIBS).exists() and LIBS not in sys.path:
    sys.path.insert(0, LIBS)

_t = os.environ.get('ATLAS_TOLERANCE', 'none').strip().lower()
TOLERANCE = None if _t in ('', 'none') else float(_t)

USED = set()      # base layers actually read (for BASES.csv and the validator)
REPAIRS = []      # geometries that needed make_valid in atlas mode


def canon(g):
    return hashlib.sha256(json.dumps(g, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def hb_path(name):
    """Path of an HB layer ('world_1938.geojson'), always the hash-verified copy in source-data/bases/hb."""
    p = BASES / 'hb' / name
    if not p.exists():
        raise FileNotFoundError(f'{p} no existe: ejecuta build/descargar_bases.py')
    USED.add('hb/' + name)
    return p


def orig_path(rel):
    """Path of a frozen original ('mapas/victoria-eje/datos/escenario.geojson')."""
    p = ORIG / rel
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def out_geometry(g):
    from shapely.geometry import mapping
    from shapely import make_valid
    if g.geom_type in ('Point', 'MultiPoint'):
        return mapping(g)
    if TOLERANCE is not None:
        return mapping(make_valid(g).buffer(0).simplify(TOLERANCE, preserve_topology=True))
    if g.is_valid:
        return _polygonal(g)
    before = canon(mapping(g))
    r = make_valid(g)
    out = _polygonal(r)
    REPAIRS.append(dict(repairedFrom=before, sha256=canon(out), reason='make_valid: geometría calculada no válida'))
    return out


def _polygonal(g):
    # Set operations can leave zero-area lines or points next to the polygons; v1 dropped them with buffer(0).
    from shapely.geometry import mapping, MultiPolygon
    if g.geom_type == 'GeometryCollection':
        polys = []
        for p in g.geoms:
            if p.geom_type == 'Polygon':
                polys.append(p)
            elif p.geom_type == 'MultiPolygon':
                polys.extend(p.geoms)
        if polys:
            return mapping(polys[0] if len(polys) == 1 else MultiPolygon(polys))
    return mapping(g)

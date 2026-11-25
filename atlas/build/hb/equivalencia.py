"""Equivalence test of the port (PLAN §6.4, task 2.3).

With ATLAS_TOLERANCE=.018 the ported generators must reproduce atlas-escenarios/dist/data exactly:
the canonical hash of every geometry and, beyond that, the whole scenario JSON. This proves the port
changes nothing but paths before the simplification is removed.

Uso:  python -I -X utf8 build/hb/equivalencia.py [ruta a atlas-escenarios/dist/data]
"""
import os, sys, json
from pathlib import Path
os.environ['ATLAS_TOLERANCE'] = '.018'
sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

DIST = Path(sys.argv[1]) if len(sys.argv) > 1 else comun.ATLAS.parents[1] / 'atlas-escenarios/dist/data'


def main():
    import v1_datos, v1_extension
    built = v1_datos.export() + v1_extension.export()
    errores = 0
    geoms = 0
    for s in built:
        ref = json.loads((DIST / (s['id'] + '.json')).read_text(encoding='utf-8'))
        # Round-trip through JSON so tuples from shapely.mapping compare as lists, as in the written files.
        mine = json.loads(json.dumps(s, ensure_ascii=False))
        g_ok = g_n = 0
        for fa, fb in zip(mine['frames'], ref['frames']):
            for a, b in zip(fa['features'], fb['features']):
                g_n += 1
                g_ok += comun.canon(a['geometry']) == comun.canon(b['geometry'])
        n_ref = sum(len(f['features']) for f in ref['frames'])
        same = mine == ref
        geoms += g_n
        ok = same and g_ok == g_n == n_ref
        errores += not ok
        print(f"{'ok   ' if ok else 'ERROR'} {s['id']:16} geometrías {g_ok}/{n_ref}  JSON completo {'idéntico' if same else 'DISTINTO'}")
    land = json.loads((DIST / 'land.js').read_text(encoding='utf-8')[len('window.ATLAS_LAND='):-1])
    same_land = comun.canon(json.loads(json.dumps(v1_datos.LAND))) == comun.canon(land)
    errores += not same_land
    print(f"{'ok   ' if same_land else 'ERROR'} land.js")
    print(f'{len(built)} escenarios, {geoms} geometrías; capas HB leídas: {", ".join(sorted(comun.USED))}')
    print('errores:', errores)
    return errores


if __name__ == '__main__':
    sys.exit(1 if main() else 0)

"""Download the base layers listed in source-data/BASES.csv and verify their sha256 (task 2.2).

Only rows with copiado=sí are kept in source-data/bases/; the rest are checked and discarded
(--todas), so a reviewer can confirm every hash in BASES.csv against the pinned commit.

Uso:  python -I -X utf8 build/descargar_bases.py [--todas] [--comprobar]
  --comprobar  no descarga: solo verifica los ficheros que ya están en source-data/bases/
"""
import csv, hashlib, sys, tempfile, urllib.request
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[1]
BASES = ATLAS / 'source-data/bases'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    todas = '--todas' in sys.argv
    solo = '--comprobar' in sys.argv
    rows = list(csv.DictReader(open(ATLAS / 'source-data/BASES.csv', encoding='utf-8')))
    errores = 0
    for r in rows:
        keep = r['copiado'] == 'sí'
        dst = BASES / r['fichero']
        if keep and dst.exists():
            ok = sha(dst.read_bytes()) == r['sha256']
            print(('ok      ' if ok else 'ERROR   ') + r['fichero'])
            errores += not ok
            continue
        if solo:
            if keep:
                print('FALTA   ' + r['fichero'])
                errores += 1
            continue
        if not keep and not todas:
            continue
        with urllib.request.urlopen(r['url'], timeout=120) as resp:
            data = resp.read()
        if sha(data) != r['sha256'] or len(data) != int(r['bytes']):
            print('ERROR   ' + r['fichero'] + ': el hash descargado no coincide con BASES.csv')
            errores += 1
            continue
        if keep:
            dst.parent.mkdir(parents=True, exist_ok=True)
            # Write to a temp file first so an interrupted run never leaves a truncated layer behind.
            with tempfile.NamedTemporaryFile(dir=dst.parent, delete=False) as t:
                t.write(data)
            Path(t.name).replace(dst)
            print('bajado  ' + r['fichero'])
        else:
            print('hash ok ' + r['fichero'] + ' (no se copia)')
    print('errores:', errores)
    sys.exit(1 if errores else 0)


if __name__ == '__main__':
    main()

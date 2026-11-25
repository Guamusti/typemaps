import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[2]
s=(root/'mapas/gran-alemania/europa_1848.html').read_text(encoding='utf-8')
for ident in ['geo','data']:
 m=re.search('<script[^>]+id=["\x27]'+ident+'["\x27][^>]*>(.*?)</script>',s,re.S)
 d=json.loads(m.group(1))
 print(ident,str(d.get('categories',{})))
 print(str(d['features'][0])[:1300].encode('ascii','backslashreplace').decode())
 (Path(__file__).parent/('gran-alemania-original.'+('geojson' if ident=='geo' else 'json'))).write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')

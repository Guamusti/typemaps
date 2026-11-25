# Atlas — contrato de datos v2

Fecha: 25-11-2026 · Dueño: orquestador (Opus) · Estado: **cerrado para las fases 2 y 3** (las decisiones P1–P9 son provisionales, ver `PLAN.md` §9).

> **v2, revisión del 25-11-2026 (primera entrega).** Con los datos reales se han hecho cambios compatibles: `patterns` lleva el marcado literal (`content`); la leyenda tiene `categories` y `original`; `color` es opcional cuando el original solo pinta una trama; se añaden `pendingYears`, `geoSha256` y `color` en los overlays; `land.js` es una `FeatureCollection`; y la descarga GeoJSON agrupa por entidad.

Este documento fija el formato de los ficheros que produce el rol de **datos** (`atlas/data/`) y que consume el rol de **front** (`atlas/index.html`). Desarrolla el borrador de `PLAN.md` §5.2. Si algún rol necesita cambiarlo, lo pide en `TAREAS.md` («Peticiones entre roles»); solo lo modifica el orquestador, que sube `schema` si el cambio no es compatible.

Ejemplo real que lo cumple: `atlas/data/_ejemplo.js` y `atlas/data/_catalogo-ejemplo.js` (§12).

---

## 1. Principios

1. **La geometría no se toca.** Cada geometría se guarda como en el original: sin `simplify`, sin redondear coordenadas (P4) y sin `make_valid` salvo reparación registrada (§7.3). Se identifica por su hash canónico.
2. **La leyenda es la original.** `category`, `color` y `pattern` son los del mapa de origen. La interfaz no los repinta con la paleta.
3. **Etapas discretas.** Cada etapa enumera todas sus entidades. No se interpola entre años.
4. **Cuatro clases que nunca se mezclan** (`kind`): historia, ucronía, extensión acumulada y prospectiva.
5. **Dos ejes independientes:** la certeza documental (`certainty`) y la precisión geométrica (`precision`).
6. **Un marcador no es una superficie** (`representation`). No se generan áreas a partir de puntos.

## 2. Ficheros

| Fichero | Contenido | Quién lo genera |
|---|---|---|
| `atlas/data/catalog.js` | `window.ATLAS_CATALOG = [ … ]`: una entrada por mapa (§3) | datos (`atlas/build/`) |
| `atlas/data/<id>.js` | `window.ATLAS_REGISTER({ … })`: un mapa completo (§4) | datos |
| `atlas/data/<id>.geo.js` | Opcional, solo si `geometries` supera ~2 MB: `window.ATLAS_REGISTER_GEO({ id, geometries })` | datos |
| `atlas/data/land.js` | `window.ATLAS_LAND = { schema: 2, collection: FeatureCollection, source: { title, path, sha256, note } }`: tierra neutra de fondo, sin significado histórico | datos |
| `atlas/data/<id>.geojson` | Descarga abierta: `FeatureCollection` con **una Feature por entidad y geometría**, con las propiedades de §6 (sin `gid`, `id` ni `certainty`), más `years` (etapas en que aparece) y `certaintyByYear`. Así no se repiten geometrías | datos |
| `atlas/data/_geometrias-origen.json` | Para cada mapa y `gid`: hash, ruta de origen dentro de `source-data/originales/` (por ejemplo `…/escenario.geojson#features[12]`) y `entityIds` | datos (generador) |
| `atlas/data/MANIFEST.json` | sha256 de cada fichero y hash canónico de cada geometría con su origen (§10) | datos (validador, tarea 2.8) |
| `atlas/data/_ejemplo.js`, `_catalogo-ejemplo.js` | Extracto real para desarrollar el front. No se enlaza desde la portada (`sample: true`) | orquestador (`atlas/_tmp/generar_ejemplo.py`) |

Formato de los `.js`:
- UTF-8 sin BOM y saltos de línea `\n`. Pueden empezar con **una** línea de comentario `// …`.
- Después solo hay una llamada: `window.ATLAS_REGISTER(` + **JSON estricto** + `);`. Sin expresiones JS, funciones ni comentarios dentro, para que el validador lo lea con un parser JSON.
- Los `.js` y `.geojson` son salidas generadas: **no se editan a mano**; se cambia el generador.

## 3. Catálogo (`ATLAS_CATALOG[]`)

| Campo | Tipo | Oblig. | Significado |
|---|---|---|---|
| `id` | string `[a-z0-9-]+` | sí | Identificador y nombre de fichero. Los que empiezan por `_` son internos |
| `kind` | `history`·`counterfactual`·`extension`·`prospective` | sí | Clase (§8.1). Decide la sección de la portada |
| `title`, `subtitle` | string | sí / no | Textos originales |
| `era`, `region` | string | sí | — |
| `years` | number[] ascendentes | sí | Años de las etapas; igual que `frames[].year` |
| `pendingYears` | `{ año: motivo }` | no | Etapas del mapa original que todavía no se han migrado, por ejemplo porque dependen de una capa de historical-basemaps. El front las muestra deshabilitadas, con el motivo |
| `divergence` | number \| null | no | Año de divergencia (ucronías) |
| `bounds` | `[[s,w],[n,e]]` | sí | Encuadre inicial en grados |
| `views` | `{ nombre: [[s,w],[n,e]] }` | no | Encuadres con nombre; por ejemplo las vistas «Europa» y «Mundo» de Carlos |
| `tags` | string[] | no | — |
| `summary`, `limits` | string | sí | Resumen y límites del escenario. `limits` se muestra siempre |
| `sources` | `[{ title, url }]` | sí | URLs `https://` |
| `license` | `[{ name, url, scope }]` | sí | Una entrada por fuente de geometría o de datos |
| `legend` | `[{ key, label, color, pattern? }]` | sí | Copia de la leyenda del mapa (§4) para las tarjetas |
| `preview` | string \| null | no | SVG de miniatura generado offline (`previews/<id>.svg`) |
| `file` | string | sí | `<id>.js` |
| `geoFile`, `geoSha256` | string | no | `<id>.geo.js` y su sha256, si existe |
| `dataSha256` | hex | sí | sha256 de los bytes de `file` |
| `sample` | boolean | no | `true` en datos de ejemplo, que no se publican |

## 4. Mapa (`ATLAS_REGISTER(payload)`)

| Campo | Tipo | Oblig. | Significado |
|---|---|---|---|
| `schema` | `2` | sí | Versión de este contrato |
| `id`, `kind` | — | sí | Los mismos que en el catálogo |
| `legend` | `[{ key, label, color?, pattern?, categories[], original? }]` | sí | Leyenda **original**, en su orden. `categories` lista los valores de `category` que cubre la entrada; por defecto `[key]`. Una entrada solo de trama (por ejemplo «expansión proyectada») lleva `categories: []` y se refiere a las entidades con ese `pattern`. Las categorías que el original dibuja pero no tienen entrada en su leyenda se añaden al final con `original: false` |
| `patterns` | `{ nombre: { width, height, rotate, content } }` | si hay tramas | Copia de los `<pattern>` del SVG o del generador original: tamaño, giro y `content`, que es el marcado interior **literal** (`<path …/>`, `<rect …/>`) |
| `style` | `{ stroke?, markerStroke? }` | no | Estilo de contorno del original, como información. El front decide según §9 |
| `roleNames` | `{ role: etiqueta }` | no | Solo si un mapa necesita una etiqueta distinta de la general (§8.2) |
| `attrLabels` | `{ clave: etiqueta }` | no | Etiquetas para mostrar `attrs` (§6). Sin ellas, el front muestra la clave |
| `sources` | `[{ title, url, note? }]` | sí | Fuentes del mapa. `sourceUrls` de las entidades apunta a estas URLs |
| `geometries` | `{ gid: GeoJSON geometry }` | sí, salvo que exista `geoFile` | Cada geometría una sola vez (§7) |
| `frames` | `Frame[]` ascendentes por `year` | sí | §5 |
| `ports`, `routes` | `Overlay[]` | sí (pueden estar vacíos) | §6.2 |
| `meta` | objeto | sí | `origin` (ruta del original), `originSha256`, `generator`, `simplified: false`, `referenceDate?`, `crs` (`EPSG:4326`) |
| `sample` | boolean | no | — |

## 5. Etapa (`Frame`)

| Campo | Tipo | Oblig. | Significado |
|---|---|---|---|
| `year` | number entero (negativo = a. C.) | sí | Único dentro del mapa |
| `title`, `text` | string | sí | Textos originales de la etapa |
| `historical` | boolean | sí | `true` = etapa de referencia real (★). Ver P2 |
| `basis` | `historical-reference`·`counterfactual-interpretation`·`cumulative-extent`·`prospective-case` | sí | Naturaleza de la etapa |
| `features` | `Feature[]` | sí | Todas las entidades visibles en esa etapa |

## 6. Entidad (`Feature`)

| Campo | Tipo | Oblig. | Significado |
|---|---|---|---|
| `id` | string | sí | Único en la etapa: `<entityId>@<year>` |
| `entityId` | string | sí | Estable entre etapas (id del original si existe) |
| `gid` | string | sí | Clave en `geometries` |
| `name` | string | sí | Nombre original |
| `category` | string | sí | Clave de la leyenda original (`core`, `hisp`, `escolon`, `plausible`…). **La leyenda y el filtro salen de aquí** |
| `color` | `#rrggbb` | sí, salvo trama sola | Color con que el original **dibujó** la entidad. Suele coincidir con el de la leyenda, pero no siempre (en 1848 los marcadores son `#176b79` sea cual sea su categoría). Si el original solo pinta una trama (`fill="url(#hatch)"` en Centrales), `color` se omite y `pattern` es obligatorio |
| `pattern` | string | no | Clave de `patterns`. Trama superpuesta al relleno, como en el original |
| `role` | §8.2 | sí | Relación de poder |
| `certainty` | `documented`·`scenario` | sí | Certeza documental del estado representado |
| `historicalBasis` | boolean | sí | `true` si la geometría reproduce un límite real documentado para la fecha de referencia de su fuente |
| `precision` | `source`·`generalized`·`approximate`·`schematic` | sí | Exactitud geométrica (§8.3) |
| `approx` | boolean | no | Campo de v1 conservado por compatibilidad. No se usa para decidir nada |
| `representation` | `area`·`location-marker` | sí | Un `location-marker` es un `Point`/`MultiPoint` y se dibuja como marcador |
| `note` | string | no | Texto de la ficha |
| `attrs` | objeto de strings | no | Propiedades originales **literales** (por ejemplo `bund`, `lenguas`, `dinastia`, `viabilidad`, `obstaculos`, `nota` en 1848) |
| `sourceUrls` | string[] | no | Subconjunto de `sources[].url` |
| `status` | string | no | Matiz libre del original (por ejemplo «protectorado») |
| `start`, `end` | number | extensión | Primer y último año de posesión |
| `period` | string | no | Texto del periodo tal como lo da la fuente |
| `lost` | boolean | extensión | `true` si en el año de la etapa ya no se posee. El front lo atenúa |

### 6.2 Puertos y rutas (`Overlay`)

`{ name, category, color, gid, note?, start?, end? }`. `color` es el que usa el generador original para ese puerto o ruta. `gid` apunta a un `Point` (puerto) o a un `LineString`/`MultiLineString` (ruta) en `geometries`. No son entidades territoriales y no cuentan como superficie. Un overlay con `start` solo se muestra desde ese año.

## 7. Geometrías

### 7.1 Tipos admitidos

`Point`, `MultiPoint`, `LineString`, `MultiLineString`, `Polygon`, `MultiPolygon` y `GeometryCollection` tal como vengan del original. No se normaliza a `MultiPolygon` porque cambiaría el hash. Leaflet dibuja todos ellos.

### 7.2 Hash canónico y `gid`

```
canon(g) = sha256( json.dumps(g, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8') )
gid      = 'g-' + canon(g)[:16]
```

- Se calcula sobre la geometría **tal como se lee del original**, sin ninguna transformación.
- Dos entidades o etapas con la misma geometría comparten `gid`. Así, en el ejemplo, Bergedorf aparece en 1848 y 1851 con una sola geometría.
- Las colisiones de 16 caracteres hexadecimales se detectan en el validador y se resuelven alargando a 24 en ese mapa.

### 7.3 Reparaciones

Si una geometría original no es válida y hace falta repararla para dibujarla, se guarda la reparada y en `MANIFEST.json` se registran `repairedFrom` (hash original), el motivo y el hash nuevo. No se repara nada que Leaflet dibuje bien.

### 7.4 Coordenadas

Lon/lat EPSG:4326 con la precisión del original (P4). Un mapa que cruce el antimeridiano conserva las coordenadas originales: el front lo resuelve al dibujar, no el generador.

## 8. Vocabularios

### 8.1 `kind`

| Valor | Sección de la portada | Etiqueta | Texto fijo en el visor |
|---|---|---|---|
| `history` | Historia | Historia | — |
| `counterfactual` | Ucronías | Ucronía | «Escenario contrafactual: lo que no ocurrió». Las etapas `historical` muestran «Referencia real» |
| `extension` | Extensión acumulada | Extensión acumulada | «Acumulado, no simultáneo: territorio que estuvo bajo este poder en algún momento» |
| `prospective` | Prospectiva | Prospectiva | El aviso del `LEEME.md` de `fronteras-2100` |

### 8.2 `role`

| Valor | Etiqueta general | Uso |
|---|---|---|
| `sovereign` | Soberanía | Soberanía reconocida, incluido el núcleo de un Estado |
| `control` | Control efectivo | Control sin reconocimiento |
| `occupation` | Ocupación | Ocupación militar o administración de ocupación |
| `dependent` | Estado dependiente | Protectorado, cliente o vasallo |
| `federal` | Miembro federal | Miembro de una federación o confederación |
| `influence` | Esfera de influencia | — |
| `claim` | Reclamación o vínculo | Reclamaciones, vínculos dinásticos, zonas discutidas |
| `project` | Proyecto no realizado | Planes que no llegaron a aplicarse |
| `case` | Caso prospectivo | Área de un caso en `prospective`. Solo se usa ahí |

El `role` de cada `category` lo fija una **tabla explícita por mapa** en `atlas/build/` (tarea 2.3), revisada por R2. Mientras no haya informe de R2 se aplica la regla de v1 (`normalize()` y el caso de 1848 de `build_data.py`), marcada como provisional en `MANIFEST.json`.

### 8.3 `precision`

| Valor | Significado |
|---|---|
| `source` | Geometría copiada sin cambios de una fuente cartográfica (HistoGIS, HB, NE) |
| `generalized` | Derivada de una fuente por unión, recorte, disolución o simplificación **hecha por el generador original** (el atlas no simplifica nada) |
| `approximate` | Trazado aproximado o marcador de posición de procedencia no documentada |
| `schematic` | Esquema deliberado (corredores, frentes orientativos) |

### 8.4 `category` en la prospectiva

En `fronteras-2101`, `category` = `level` original (`context`, `process`, `plausible`, `uncertain`) y `role` = `case`. La leyenda muestra los niveles.

## 9. Reglas para el front

- **Carga:** antes de insertar `<script src="data/<id>.js">` se define `window.ATLAS_REGISTER = payload => …`. Si el catálogo trae `geoFile`, se carga también y se espera a `ATLAS_REGISTER_GEO` antes de dibujar. Solo se carga el mapa abierto.
- **Colores:** relleno = `feature.color`; trama = `patterns[feature.pattern]` encima del relleno; marcadores = círculo con `color` y contorno `style.markerStroke` si existe. La paleta `mapeo.cfg` solo afecta a `--bg` (mar), `--land` (tierra neutra de `land.js`), `--line` (contornos) y `--accent` (selección).
- **Leyenda:** por `legend` (orden original) y filtrable por `category`. El `role` aparece en la ficha y en un filtro secundario, nunca sustituye a la leyenda.
- **Ficha:** `name`, etiqueta de `role`, `certainty` y `precision` como textos separados, `note`, `attrs` (con `attrLabels`), `period`/`start`/`end`, enlaces `sourceUrls`.
- **Etapas:** el cambio de etapa sustituye las entidades; no hay transición de formas. Con `prefers-reduced-motion` no hay ninguna animación.
- **Sin datos inventados:** el front no calcula áreas, no une geometrías y no convierte marcadores en superficies.

## 10. Validación (tarea 2.8, bloquea la integración)

El validador de `atlas/build/` comprueba, como mínimo:

1. Que cada `.js` es `ATLAS_REGISTER(` + JSON válido y que su sha256 coincide con `dataSha256`.
2. Que todo `gid` existe en `geometries` y que `gid == 'g-' + canon(geometry)[:16]`.
3. Que el hash canónico de cada entidad coincide con el del original, salvo las reparaciones registradas (§7.3).
4. Que el número de entidades por mapa y etapa coincide con el original, incluidas las 24 `context` de 1848.
5. Que cada `location-marker` es un punto, y que no aparece ningún área sin fuente.
6. Que cada `category` existe en `legend` y que su color coincide con el del original.
7. Que `kind`, `role`, `certainty`, `precision`, `representation` y `basis` están en los vocabularios de §8.
8. Que los años están ordenados y coinciden con `years`, y que las URLs son `https://`.

Escribe `MANIFEST.json`: `{ files: { ruta: sha256 }, geometries: { gid: { sha256, origin, entityIds[], repairedFrom? } }, roleTables: { id: 'provisional'|'R2' } }`.

## 11. Compatibilidad con v1 (`atlas-escenarios`)

| v1 | v2 |
|---|---|
| `features[].geometry` repetida en cada etapa | `gid` + `geometries` únicas |
| `role` heurístico; color `#ac8972` en lugar de `url(#hatch)` | `category` + `color` + `pattern` originales; `role` por tabla |
| `approx` | `precision` (`approx` se conserva) |
| `originalCategory` (solo 1848) | `category` (siempre) |
| Sin `kind`; la prospectiva usa `claim` | `kind` obligatorio; la prospectiva usa `case` |
| `ports[]` con `lat`/`lon` | `ports[]` con `gid` |

El front no tiene que leer v1.

## 12. Ejemplo: `atlas/data/_ejemplo.js`

Lo genera `atlas/_tmp/generar_ejemplo.py` directamente desde el GeoJSON incrustado en `mapas/gran-alemania/europa_1848.html`. Los textos los copia de `build_data.py` y las tramas y colores dibujados, del SVG del original.

- 8 geometrías sin simplificar, cuyo hash coincide con el del original (el script lo comprueba al final): Bergedorf, Bremen, Liechtenstein y Lauenburg (con la trama `diagonal`), Eslavonia civil, San Marino, y los marcadores de Limburgo y Venlo.
- Contiene 5 categorías (`core`, `exception`, `dynasty`, `context`, `uncertain`) de las 8 de la leyenda, que se incluye completa. Tiene los roles `sovereign` y `claim`, dos representaciones (`area` y `location-marker`) y dos precisiones (`source` y `approximate`).
- Hay dos etapas:
  - **1848**, histórica y `documented`: 6 entidades.
  - **1851**, ucronía y `scenario`: 8 entidades. Las 6 primeras reutilizan los mismos `gid`.
- Pesa 33 KB. Su sha256 aparece en `_catalogo-ejemplo.js`.

Solo aparecen 2 de los 9 roles porque el original de 1848 no tiene otros, y añadirlos sería inventar. Para probar el resto, el front usa los vocabularios de §8.

## 13. Dudas anotadas (decisión provisional y conservadora)

- **C1.** Las entidades `context` de 1848 llevan `role: sovereign`, como el resto según la regla de `build_data.py`. Lo revisará R2.
- **C2.** En las etapas no históricas, `certainty` vale `scenario` para todas las entidades, incluidas las de contexto, como en v1 (la regla es de etapa). Si R1 propone que sea por entidad, se cambia el generador, no el contrato.
- **C3.** Los marcadores del original no indican su procedencia, así que se les asigna `precision: approximate`.
- **C4.** `historicalBasis` cambia de significado respecto a v1: en v1 dependía de la etapa y en el mapa de 1848 siempre era `false`. Ahora significa «la geometría reproduce un límite documentado». Hay que confirmarlo con R1.
- **C5.** La licencia de HistoGIS y HGIS Germany se verificará en la tarea 2.9. Mientras tanto, el catálogo de ejemplo pone «Por verificar».
- **C6.** `style.stroke` (`#857e76` en 1848) se guarda como información. El front dibuja los contornos con `--line` (§5.4 del plan), así que el aspecto no es idéntico al original. Si Marcos prefiere el contorno original, solo hay que cambiar el front.

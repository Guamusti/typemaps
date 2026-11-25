# Atlas — fase 0: inventario y plan

Fecha: 25-11-2026 · Autor: orquestador (Opus) · Estado: **propuesta, pendiente del visto bueno de Marcos**.

En esta fase solo se ha leído. No se ha modificado ningún original, no hay commits ni push, y no se ha arrancado ningún servidor (en el puerto 4173 no escuchaba nada y la revisión no lo necesitaba). Se han escrito únicamente `atlas/PLAN.md`, `atlas/INVENTARIO.csv`, `atlas/TAREAS.md` y los auxiliares de `atlas/_tmp/` (§10).

---

## 1. Inventario verificado

### 1.1 Cifras comprobadas

| Comprobación | Resultado |
|---|---|
| `npm run check` (catálogo principal) | 8 mapas, 31 etapas, sin errores |
| `node scripts/check-extension.cjs` | 11 mapas (8 de extensión + 3 alternativos), 60 etapas |
| `audit_data.py` (copia que escribe en `atlas/_tmp/`) | **19 mapas, 91 etapas, 3168 instancias, 0 errores**; informe idéntico byte a byte al `AUDITORIA-DATOS.json` guardado |
| Ficheros inventariados | 231 filas en `INVENTARIO.csv`: 211 ficheros, 6 auxiliares de `_tmp/`, 1 fila resumen de `.libs/` (1792 ficheros vendorizados) y 13 referencias inaccesibles |

`atlas-escenarios/README.md` (7 escenarios, 27 etapas) y `dist/data/manifest.json` (8 y 31) están desfasados. La referencia son los dos catálogos.

`audit_data.py` necesita Python 3.12, porque Shapely está compilado como cp312 en `mapas/potencias-centrales/.libs`, y el Python del sistema es el 3.11. Se usó el intérprete 3.12 de Codex (`C:\Users\marco\.cache\codex-runtimes\...\python.exe`).

### 1.2 Los 19 mapas

| id | Título | Clase | Etapas (★ = referencia `historical`) | Fuente vectorial original | Salida en `atlas-escenarios/dist` |
|---|---|---|---|---|---|
| `carlos` | La herencia de Carlos | ucronía | 1556, 1580, 1600, 1640 | `mapas/monarquia-universal/datos/escenario.geojson` (18 entidades, 2362 vértices) + `puertos_y_rutas.json` + `world_1600.geojson` (Sacro Imperio) | simplificada |
| `centrales` | Victoria de las Potencias Centrales | ucronía | 1914★, 1918, 1920, 1925 | `mapas/potencias-centrales/datos/escenario.geojson` (80 entidades, 9302 vértices) + `world_1914` | simplificada |
| `eje` | Victoria del Eje en Europa | ucronía | 1938★, 1942, 1944, 1948 | `mapas/victoria-eje/datos/escenario.geojson` (95 entidades, 10 890 vértices) + `world_1938`/`1994` | simplificada |
| `gran-alemania` | La solución granalemana | ucronía | 1848★, 1849, 1851 | GeoJSON incrustado en `mapas/gran-alemania/europa_1848.html` (`script#geo`, 91 entidades; `script#data`, 8 categorías y 13 fuentes) | simplificada; además **descarta las 24 entidades `context`** |
| `japon` | Victoria japonesa en Asia-Pacífico | ucronía | 1938★, 1940, 1943, 1948 | No hay original independiente: lo construye `build_data.py` con las capas HB de 1938 y 1994. El original de ChatGPT no es accesible (§2) | simplificada |
| `gran-colombia` | La Gran Colombia federal | ucronía | 1819, 1822, 1830, 1850 | `build_data.py` + HB 1994 | simplificada |
| `kalmar` | La Unión de Kalmar perdura | ucronía | 1520, 1523, 1536, 1600 | `build_data.py` + `source-data/world_1530.geojson` | simplificada |
| `mexico-norte` | México conserva su norte | ucronía | 1822★, 1836, 1848, 1880 | `build_extension.py` + HB | simplificada |
| `centroamerica` | Centroamérica unida | ucronía | 1824★, 1838, 1860, 1914 | `build_extension.py` + HB | simplificada |
| `tres-naciones` | La Mancomunidad de las Tres Naciones | ucronía | 1650★, 1658, 1667, 1700 | `build_extension.py` + HB | simplificada |
| `max-espana` | Todo lo que fue español | extensión acumulada | 7 cortes, de 1500 a 1976 | `build_extension.py` + `extension_complementos.py` + `source-data/hb/` | simplificada; 188 marcadores |
| `max-portugal` | Todo lo que fue portugués | extensión acumulada | 6 cortes, de 1460 a 1999 | ídem | simplificada; 171 marcadores |
| `max-iberia` | Los dos imperios ibéricos | extensión acumulada | 5 cortes, de 1500 a 1999 | ídem | simplificada |
| `max-britanico` | Todo lo que fue británico | extensión acumulada | 6 cortes, de 1650 a 1997 | ídem | simplificada |
| `max-frances` | Todo lo que fue francés | extensión acumulada | 6 cortes, de 1700 a 1980 | ídem | simplificada |
| `max-roma` | Todo lo que fue romano | extensión acumulada | 6 cortes, de −201 a 1453 | ídem | simplificada |
| `max-mongol` | Todo lo que fue mongol | extensión acumulada | 6 cortes, de 1206 a 1480 | ídem | simplificada |
| `max-otomano` | Todo lo que fue otomano | extensión acumulada | 6 cortes, de 1453 a 1922 | ídem | simplificada |
| `fronteras-2101` | Fronteras hacia el siglo XXII | prospectiva | 2026★, 2035, 2050, 2101 | `mapas/fronteras-2100/fronteras-2101.geojson` (38 casos) y `escenario.json`; los genera `casos.py`/`generar.py` a partir de Natural Earth | **sin simplificar**: geometrías idénticas a `escenario.json` |

Los 10 escenarios alternativos del encargo coinciden con los 10 marcados como ucronía, y los 8 de extensión también. En los 8 de extensión todas las entidades son `documented`.

### 1.3 Formatos y ubicaciones

- **`mapas/<mapa>/`**: el HTML interactivo con un SVG proyectado incrustado; en Gran Alemania, además, el GeoJSON incrustado. También hay SVG y PNG de render, `generar.py`, `verificar.cjs` y `datos/` (GeoJSON en lon/lat sin simplificar más capas de historical-basemaps). Proyecciones de los renders: LCC en Europa, Equal Earth en la vista mundial de Carlos y EPSG:3035 en el mapa de 1848.
- **`atlas-escenarios/dist/data/`**: cada mapa en tres formatos (`.js` con `ATLAS_REGISTER`, `.json` completo y `.geojson` con la última etapa), además de `catalog*.js|json`, `land.js` y `manifest.json`.
- **`atlas-escenarios/dist/previews/`**: 19 miniaturas SVG proyectadas.
- **`atlas-escenarios/dist/prospectiva/`**: copia de `mapas/fronteras-2100`. Su `index.html` solo difiere de `mapa.html` en las rutas de `vendor/`.
- **`atlas-escenarios/source-data/`**: 17 capas HB en `hb/`, `world_1530` y copias de los `datos/` de tres mapas.
- **`chats/`**: 9 conversaciones; de las 7 primeras hay copia en `.md` y en `.json`.

---

## 2. Estado del material

| Estado | Material |
|---|---|
| **Ya recuperado** (en `Mapas/`) | Los 4 originales cartográficos y el de prospectiva (§1.2), sus generadores, las bases HB y Natural Earth, la app completa y 9 chats de texto. |
| **Recuperado en esta fase** | `atlas/_tmp/despliegue-anterior/index.html` (sha256 `871fd769…9965`, 882 659 B), descargado de https://atlas-historia-europa.vercel.app/ y no ejecutado. Es un atlas de **historia real 1783–1945** («1789–1945 · Atlas de historia europea»): 11 cortes de historical-basemaps (1783, 1800, 1815, 1878, 1880, 1900, 1914, 1920, 1930, 1938, 1945) como trazados SVG **ya proyectados** (Lambert azimutal equivalente, 15° E y 52° N) en `atlasGeometry`, más `atlasMaps`, un módulo de la Primera Guerra Mundial (bando de cada país de 1914 a 1918), batallas, sucesos y épocas (Napoleón, Sacro Imperio, unificaciones, 1GM, entreguerras, 2GM). Licencia GPL-3.0. **No contiene el mapa granalemán de 1848.** |
| **Recuperable fuera del alcance actual** | Las «dos copias de Descargas» de `europa_1848.html` (lo dice el README de la raíz). Esta fase no salía de `Mapas/` y no se buscó en Descargas. Las capas HB se pueden volver a descargar, pero falta fijar el commit (§9). |
| **Inaccesible** (solo hay referencias; **no** se presenta como recuperado) | `sandbox:/workspace/scratch/42da5c2cba6d/japon_escenario/dist/japon_victoria_asia_pacifico.html`, `.svg` y `atlas_victoria_japonesa.zip` (citados en chats/01); `sandbox:/mnt/data/Emblema circular de cuatro cuadrantes.png` (chats/07); `/workspace/scratch/42da5c2cba6d/mapa1848*` y `/workspace/scratch/30ddd4b5941c/` (sin ninguna referencia en `chats/`); `atlas_1848_revision_2.zip`, `atlas_gran_alemania_1848.zip`, `centroeuropa_1848.html`, `europa_1848.svg`, `europa_1848_solo_mapa.png` y `ww1-interactivo.html` (sin copia en `Mapas/`). El contenido de la Primera Guerra Mundial parece haber acabado dentro del despliegue anterior, pero no se puede afirmar que sea el mismo `ww1-interactivo.html`. |

---

## 3. Duplicados y versión recomendada

### 3.1 Duplicados exactos (SHA-256)

| Contenido | Copias idénticas | Se conserva |
|---|---|---|
| `fronteras-2101.geojson`, `LEEME.md` y `mapa-datos.js` | `mapas/fronteras-2100/` = `atlas-escenarios/dist/prospectiva/` | `mapas/fronteras-2100/` |
| `escenario.geojson` de Carlos, Centrales y Eje; `puertos_y_rutas.json` | `mapas/<x>/datos/` = `atlas-escenarios/source-data/mapas/<x>/datos/` | `mapas/<x>/datos/` |
| `world_1914`, `world_1938`, `world_1994` y `world_1600` | 2 o 3 copias en `mapas/*/datos` y `source-data` | una copia por año y hash |
| Licencia GPL-3.0 de HB | 4 copias | una |

### 3.2 Casi duplicados (mismo contenido, otro formato)

- `dist/data/<id>.js`, `.json` y `.geojson` contienen el mismo escenario: el `.js` lleva `ATLAS_REGISTER` y el `.geojson` solo la última etapa.
- `scripts/gran-alemania-original.geojson|json` reproduce **exactamente** el JSON incrustado en `europa_1848.html` (igualdad comprobada al parsear).
- `dist/prospectiva/index.html` es `mapa.html` con otras rutas de vendor.

### 3.3 Versión recomendada de cada mapa

Medición de `atlas/_tmp/comparar_geometrias.py` (salida en `comparar_geometrias.txt`):

| Mapa | Vértices: original → dist | Diferencia simétrica de área (mediana / máx.) | Hausdorff máx. |
|---|---|---|---|
| carlos | 2362 → 2218 | 0,21 % / 0,59 % | 0,018° |
| centrales | 9302 → 6261 | 0,46 % / 46 % («Territorio sin identificar») | 0,019° |
| eje | 10 890 → 6664 | 0,48 % / 32 % | 0,028° |
| gran-alemania (sin `context`) | **46 386 → 10 349** | **4,99 % / 29 %** (Fráncfort; Hamburgo, Lübeck y Bergedorf entre el 23 y el 26 %) | 0,027° |
| fronteras-2101 | idénticos | 0 | 0 |

**Recomendación:** migrar siempre desde el **original vectorial** y nunca desde `dist/`. `build_data.py` y `build_extension.py` aplican `simplify(.018)` (~2 km) a todo polígono, y `normalize()` además pierde la categoría original (por ejemplo, «Estado vinculado a Alemania · hipótesis» pasa a `sovereign`) y sustituye las tramas `url(#hatch)` por el color plano `#ac8972`. Eso contradice la regla de conservar fronteras y leyendas.

| Mapa | Versión que se migra | Por qué |
|---|---|---|
| gran-alemania | `europa_1848.html` (GeoJSON incrustado), con la extracción `gran-alemania-original.*` como entrada equivalente | Es la única fuente completa: 91 entidades, 8 categorías con su color, 13 fuentes y metadatos. Hay que recuperar las 24 de `context`. La vista centroeuropea no está disponible; si aparece, se conserva como **vista** (encuadre y etiquetas), no como duplicado. |
| carlos, centrales, eje | `mapas/<x>/datos/escenario.geojson` + capas base + `generar.py` (colores, leyenda y tramas) | Sin simplificar; conserva `cat`/`kind`/`category`/`project`. Las vistas «Europa» y «Mundo» de Carlos pasan a ser dos encuadres de un mismo mapa. |
| japon, gran-colombia, kalmar, mexico-norte, centroamerica, tres-naciones y los 8 `max-*` | Los generadores portados **sin** simplificar, sobre las mismas capas HB (fijadas por hash) | No existe otro original. `dist/` queda como referencia visual v0. |
| fronteras-2101 | `mapas/fronteras-2100/escenario.json` + `fronteras-2101.geojson` | Ya está sin simplificar. Hay que recuperar el significado de `level` (context/process/plausible/uncertain) que el visor genérico pierde. |

---

## 4. Clasificación (`kind`)

| kind | Mapas | Observaciones |
|---|---|---|
| `history` (historia real) | Ninguno de los 19 en su conjunto. Lo son las etapas ★ de referencia y el **despliegue anterior** (1783–1945), que podría incorporarse en una fase opcional. | — |
| `counterfactual` (ucronía) | carlos, centrales, eje, gran-alemania, japon, gran-colombia, kalmar, mexico-norte, centroamerica, tres-naciones | Hoy `build_data.py` fija `certainty` según la etapa (`historical`). Carlos 1556, Kalmar 1520 y Gran Colombia 1819/1822 describen situaciones reales, pero llevan `scenario`. Lo revisará el rol histórico (R1). |
| `extension` (extensión acumulada) | los 8 `max-*` | Todo es `documented`, pero se trata de territorio que estuvo bajo ese poder **en algún momento**, no a la vez. La interfaz debe decirlo siempre, y `lost` debe verse. |
| `prospective` (prospectiva) | fronteras-2101 | Hoy no tiene `kind` y sus 152 instancias son `claim`. El visor genérico lo trata como historia alternativa (lo reconoce `COORDINACION-CLAUDE.md`). |

---

## 5. Arquitectura dentro de typemaps

### 5.1 Motor: Leaflet local frente al SVG propio de mapeo

| | Leaflet 1.9.4 en `atlas/vendor/leaflet/` | SVG propio como en `mapeo/` |
|---|---|---|
| Datos | GeoJSON lon/lat tal cual: es el formato de todos los originales | `mapeo/hist/eYYYY.js` guarda trazados **ya proyectados** (`"d":"M541.7,…"`); reutilizarlo obliga a proyectar al generar y a perder lon/lat en el cliente |
| Zoom a estados diminutos (Bergedorf, Fráncfort, enclaves) | Nativo, sin límite práctico | Hay que implementar zoom, pan y reproyección |
| Puntos, rutas y antimeridiano | Ya resuelto en `atlas-escenarios` | Hay que hacerlo |
| Proyección | Web Mercator: distorsiona Escandinavia, Rusia y las vistas mundiales | Libre (LCC o Equal Earth, como en los originales) |
| Peso | ~150 KB más CSS, con licencia BSD-2 | 0 KB, pero más código propio |
| Coherencia con typemaps | Distinto de mapeo | Igual que mapeo |

**Recomendación (la opción conservadora):** usar Leaflet local con GeoJSON lon/lat y sin teselas de terceros; el fondo sería `land` dibujado con `--land`. Es lo único que garantiza que la geometría servida sea byte a byte la del original y que ya funciona con estos datos. Las miniaturas de las tarjetas serían SVG proyectados generados offline. Una proyección equivalente con Proj4Leaflet queda como decisión de Marcos (P3).

### 5.2 Contrato de datos (borrador v2; lo fija el orquestador en la tarea 1)

Es una ampliación compatible del contrato `ATLAS_REGISTER` actual.

**Catálogo** `atlas/data/catalog.js` → `window.ATLAS_CATALOG = [ { … } ]`
`id, kind ('history'|'counterfactual'|'extension'|'prospective'), title, subtitle, era, region, years[], divergence, bounds [[s,w],[n,e]], views {nombre: bounds}, tags, summary, limits, sources[{title,url}], license[{name,url,scope}], legend[{key,label,color,pattern?}], preview, file, dataSha256`.

**Mapa** `atlas/data/<id>.js` → `window.ATLAS_REGISTER({ schema: 2, id, kind, legend, roleNames, geometries, frames, ports, routes })`

- `geometries`: `{ gid: GeoJSON geometry }`. Cada geometría se guarda **una sola vez**, sin simplificar y con la precisión de coordenadas del original. `gid` = `g-` + 16 primeros caracteres del sha256 canónico (§8).
- `frames[]`: `{ year, title, text, historical, basis, features[] }`. **No se interpola**: cada etapa enumera sus entidades.
- `features[]`: `{ id, entityId, gid, name, category, color, pattern?, role, status?, certainty, historicalBasis, precision, representation, note, sourceUrls[], start?, end?, period?, lost? }`
  - `category` es la clave de leyenda **original** (por ejemplo `core`, `east`, `reich`, `ally`, `hisp`, `escolon`, `plausible`) y es obligatoria. La leyenda sale de `category`, no de `role`.
  - `color` y `pattern` son los originales (`pattern: 'hatch'|'project'|'frontier'` reproduce las tramas SVG).
  - `role` describe la relación de poder y separa: `sovereign` (soberanía reconocida), `control` (control efectivo sin reconocimiento), `occupation`, `dependent`, `federal`, `influence`, `claim` (reclamación), `project` (plan no realizado, como los del Eje) y `case` (área de un caso prospectivo).
  - `certainty` (`documented`/`scenario`) es la certeza documental. `precision` (`source`/`generalized`/`approximate`/`schematic`) sustituye a `approx` sin retirarlo y describe la exactitud geométrica. Son dos ejes independientes.
  - `representation`: `area` o `location-marker`. Un marcador nunca se convierte en superficie.
- `land.js` y `meta`: procedencia de la base y su hash.

**Descargas abiertas:** `atlas/data/<id>.geojson`, con todas las etapas y la propiedad `year`, para quien quiera los datos fuera del visor.

### 5.3 Navegación

- `atlas/index.html` es una sola página. La portada tiene tarjetas agrupadas en cuatro secciones (**Historia · Ucronías · Extensión acumulada · Prospectiva**), cada una con una etiqueta visible del tipo.
- El visor se abre con `#/<id>/<año>`, que se puede compartir. Carga bajo demanda `data/<id>.js`.
- Tiene línea del tiempo discreta (←/→, Inicio/Fin), leyenda filtrable por `category`, ficha de entidad, fuentes, licencias, encuadres (`views`) y descarga del GeoJSON.
- En la extensión acumulada, el texto fijo «acumulado: no simultáneo» y `lost` atenuado. En prospectiva, el aviso de `LEEME.md` y los niveles en lugar de roles.
- Funciona con teclado y foco visible, y respeta `prefers-reduced-motion` (sin animar el paso de etapa).
- Se enlaza desde `typemaps/index.html` solo cuando Marcos lo pida (AGENTS.md).

### 5.4 Paleta compartida

- El cromo de la interfaz lee `localStorage['mapeo.cfg']` (`palette` y `custom`) y aplica `--bg --alt --text --sub --accent --err`. Además deriva, igual que mapeo, `--line: color-mix(in srgb,var(--sub) 30%,transparent)` y `--land: color-mix(in srgb,var(--sub) 30%,var(--bg))`.
- `PALETTES` está definida dentro de `mapeo/index.html`, y `mapeo/` no se toca. Por eso el atlas lleva una **copia literal** de la tabla y un test comprueba que coincide con la de mapeo (P5: ¿extraerla a un `/paleta.js` común?).
- **Los colores de los datos no se repintan con la paleta**: son significado de leyenda. Con la paleta solo cambian el mar (`--bg`), la tierra neutra (`--land`), los contornos (`--line`) y la selección (`--accent`). Con paletas oscuras se refuerza el contorno de las entidades con `--line` y no se toca su relleno.
- La tipografía es Instrument Serif en titulares y JetBrains Mono en el texto, como en el resto del sitio.

---

## 6. Migración

1. **Congelar los originales (datos, tarea 2.1).** Se copian a `atlas/source-data/originales/<mapa>/`, con la estructura relativa, todos los ficheros `original-*`, `licencia`, generadores y documentación marcados así en `INVENTARIO.csv`. Se escribe `originales/MANIFEST.csv` (ruta de origen, ruta de copia y sha256) y se comprueba que cada copia tiene el mismo hash que su origen. No se copian `.libs/`, el hosting privado ni los chats (P6).
2. **Bases cartográficas (tarea 2.2).** Para las capas HB y Natural Earth se registran la URL, el commit o versión y el sha256 en `atlas/source-data/BASES.csv`. Se copian al repo solo las que use el generador; el `admin_1` de 40 MB, solo si se decide (P7). Un script de descarga verifica los hashes.
3. **Generador portado (tarea 2.3)** en `atlas/build/`, Python 3.12 + Shapely, ejecutado offline; sus salidas se versionan. Se parte de `build_data.py`, `build_extension.py` y `extension_complementos.py` con estos cambios:
   - `TOLERANCE = None` por defecto (sin `simplify`). `make_valid` solo se aplica a geometrías inválidas, y se registran los dos hashes.
   - Una tabla explícita por mapa `categoría original → role`, revisada por el rol histórico, en lugar de la heurística de `normalize()`.
   - Se recuperan `category`, color, `pattern` y la leyenda de `generar.py` o de `data.categories`, más las entidades `context` de 1848.
   - Cada etapa referencia `gid`; las geometrías no se duplican.
4. **Prueba de equivalencia antes del cambio:** con `TOLERANCE=.018` y la heurística antigua, el generador portado tiene que reproducir los hashes de geometría de `dist/data/*.json`. Así se demuestra que el port no altera nada más. Después se quita la simplificación.
5. **Metadatos:** se conservan `sources`, `sourceUrls`, `limits`, `note`, `historicalBasis`, `validAt`, `entityId` y los demás campos actuales. Se añade `license` por fuente, y `atlas/CREDITS.md` reúne HB (GPL-3.0), Natural Earth (dominio público), HistoGIS/HGIS/IEG (cada una con su licencia; IEG CC BY-NC solo como referencia documental) y Leaflet (BSD-2).
6. **Tamaño:** solo se carga el mapa que se abre. Si una geometría supera ~2 MB (previsiblemente Gran Alemania y la base de prospectiva), se separa `geometries` en `data/<id>.geo.js`. Para reducir decimales hace falta el permiso de Marcos (P4).

---

## 7. Fases, dependencias y roles

| Fase | Tareas (detalle en `TAREAS.md`) | Rol y modelo | Depende de |
|---|---|---|---|
| 0 | Inventario y plan | Orquestador · Opus | — (**hecha**) |
| 1 | Contrato v2 cerrado, datos de ejemplo (`atlas/data/_ejemplo.js`) y decisiones P1–P8 | Orquestador · Opus | Visto bueno de Marcos |
| 2 | 2.1 congelar originales · 2.2 bases · 2.3 generador y prueba de equivalencia · 2.4 los cuatro originales a resolución completa · 2.5 ucronías derivadas de HB · 2.6 extensión acumulada · 2.7 prospectiva · 2.8 validador de hashes · 2.9 `CREDITS.md` | Datos · Codex (worktree `atlas-datos`) | 1 (la 2.1 y la 2.2 pueden empezar con la fase 0 aprobada) |
| 3 | 3.1 estructura y paleta · 3.2 visor Leaflet · 3.3 leyenda, roles y fichas · 3.4 línea del tiempo y teclado · 3.5 distinción por `kind` · 3.6 móvil, accesibilidad y movimiento reducido | Front · **solo Opus** (worktree `atlas-front`) | 1 (trabaja con `_ejemplo.js`; en paralelo con la 2) |
| 4 | R1 clases y etapas `historical` · R2 tablas categoría → role · R3 extensión (omisiones y `lost`) · R4 redacción de la prospectiva | Revisión · Gemini (solo lectura; escribe en `atlas/revision/`) | Salidas de la 2.3 a la 2.7 |
| 5 | Integración de ramas, validación del §8 y petición de aprobación | Orquestador · Opus | 2, 3 y 4 |
| 6 (opcional) | Historia real 1783–1945 a partir del despliegue anterior: regenerar desde HB en lon/lat (no desde los trazados proyectados) y conservar sus textos de sucesos | Datos + Front | 5 y decisión P8 |

Coordinación según AGENTS.md: un rol que necesite un cambio en ficheros de otro lo anota en `TAREAS.md`. `delegate_task` solo se usa para tareas cortas.

---

## 8. Validación

**Hash canónico de geometría:** `sha256(json.dumps(geometry, sort_keys=True, separators=(',',':'), ensure_ascii=False))`, sin ninguna transformación previa.

- **Geográfica (bloquea la integración):**
  - Por cada entidad migrada se compara el hash canónico en origen y en `atlas/data`: deben coincidir, salvo una lista explícita de geometrías reparadas con `make_valid`, que llevan los dos hashes.
  - Mismo número de entidades por mapa y etapa que en el original, incluidas las 24 `context` de 1848.
  - Los puntos siguen siendo puntos: el número de marcadores es el mismo y no aparece ningún polígono nuevo sin fuente.
  - Diferencia de área y Hausdorff = 0. La línea base de hoy está en `atlas/_tmp/comparar_geometrias.txt`.
  - Una salida de `atlas/data/MANIFEST.json` con el sha256 de cada fichero y de cada geometría.
- **Leyenda:** cada `category` y su color coinciden con `generar.py`/`data.categories`, y las tramas (`hatch`, `project`, `frontier`) se mantienen.
- **Funcional:**
  - Un `check.cjs` ampliado al esquema v2 (roles, `kind`, años ordenados, `gid` resueltos, HTTPS en fuentes).
  - Carga de los 19 mapas y de todas sus etapas sin errores de consola.
  - Las URLs `#/<id>/<año>` funcionan, se puede navegar con teclado y se respeta `prefers-reduced-motion`.
- **Visual:** captura de cada mapa en el encuadre del original, al lado de los PNG originales (`comprobacion-*.png`, `europa_victoria_*.png`), en una paleta oscura y en una clara, más el móvil a 390 × 844. La comparación es lado a lado, no por píxeles, porque cambia la proyección.
- **Histórica:** informes de Gemini en `atlas/revision/` (R1 a R4). Ningún cambio de `kind`, `historical` o `role` se integra sin su informe.
- **Licencias:** cada fuente aparece en `CREDITS.md` y en el `license` del catálogo.

---

## 9. Riesgos, decisiones pendientes y archivos que faltan

### Riesgos

1. **Pérdida de precisión** si alguien migra desde `dist/` por comodidad. Se mitiga con la regla del §3.3 y el validador de hashes.
2. **GPL-3.0:** las capas HB, y con ellas todo lo que derive de ellas, son GPL-3.0. Mapeo ya usa HB, así que es coherente, pero hay que avisarlo en `CREDITS.md` y ofrecer los datos. El despliegue anterior también es GPL-3.0.
3. **Peso:** Gran Alemania a resolución completa ronda los 3,3 MB en GeoJSON, frente a 0,5 MB hoy.
4. **El commit de HB no está registrado** en `source-data/hb` (el despliegue anterior cita da7a4b7). Una nueva descarga podría traer geometrías distintas.
5. **El entorno Python 3.12 depende de la carpeta `.libs` de otro proyecto.** Conviene un `requirements` con versiones fijadas.
6. **Mercator** desfigura las vistas mundiales y nórdicas.
7. **Mezcla de semánticas:** hoy `certainty` depende de la etapa y no de la entidad, y la prospectiva usa `claim`. La revisión R1/R2 es imprescindible.
8. **Solapamiento con mapeo**, que ya tiene 22 cortes históricos de HB proyectados. El atlas no debe duplicar su papel de juego.

### Decisiones pendientes para Marcos (preguntas abiertas)

Ante la duda se ha tomado la opción conservadora que se indica entre paréntesis.

- **P1.** ¿Se puede buscar en Descargas y en otras carpetas fuera de `Mapas/` (las dos copias de `europa_1848.html`, `centroeuropa_1848.html`, los zip de 1848 y `ww1-interactivo.html`)? (No se ha buscado.)
- **P2.** ¿Las etapas reales dentro de una ucronía (Carlos 1556, Kalmar 1520, Gran Colombia 1819/1822) se marcan como `historical`? (Se mantienen como están hasta R1.)
- **P3.** ¿Mercator en Leaflet o una proyección equivalente con Proj4Leaflet, que es otra dependencia? (Mercator.)
- **P4.** ¿Se permite redondear coordenadas para ahorrar peso? (No: precisión original.)
- **P5.** ¿Se extrae la tabla `PALETTES` a un fichero común, lo que toca `mapeo/`? (No: copia literal en el atlas con un test de igualdad.)
- **P6.** ¿Se publican en el repo los originales y los chats? `atlas/source-data/` lo despliega Vercel salvo que se añada un `.vercelignore` en la raíz. (Se copian los originales cartográficos tal como exige AGENTS.md; los chats no; no se crea `.vercelignore` sin permiso.)
- **P7.** ¿Se versiona el `ne_10m_admin_1` de 40 MB o se registra solo su hash y su URL? (Solo hash y URL.)
- **P8.** ¿Se incorpora el atlas de historia real 1783–1945 (fase 6)? (Queda fuera hasta que se decida.)
- **P9.** ¿Se puede retirar el visor genérico de `atlas-escenarios`, o tiene que seguir vivo en paralelo? (Sigue intacto; no se toca.)

### Archivos que faltan

El original japonés de ChatGPT (HTML, SVG y zip), el emblema del atlas (PNG), `centroeuropa_1848.html`, `europa_1848.svg`, `europa_1848_solo_mapa.png`, `atlas_1848_revision_2.zip`, `atlas_gran_alemania_1848.zip`, `ww1-interactivo.html`, el contenido de `/workspace/scratch/42da5c2cba6d/mapa1848*` y de `/workspace/scratch/30ddd4b5941c/`, y el commit de HB de `source-data/hb`. Todos figuran en `INVENTARIO.csv` con el estado `inaccesible`.

---

## 10. Ficheros auxiliares (`atlas/_tmp/`, se pueden borrar)

- `generar_inventario.py`: genera `INVENTARIO.csv` (solo lee los originales).
- `comparar_geometrias.py` y `comparar_geometrias.txt`: medición original frente a `dist`.
- `audit_copia.py` y `AUDITORIA-DATOS.json`: ejecuta `audit_data.py` sin cambiarlo, con el informe redirigido aquí (idéntico al original).
- `despliegue-anterior/index.html`: copia del sitio anterior. No se ha ejecutado.

Nota: antes del corte, en la sesión anterior, se escribió en la carpeta Temp de la sesión (`…\scratchpad\hashes.json` y `audit\`). Esos ficheros no se usan y se han rehecho dentro de `atlas/_tmp/`.

---

## Resumen (una página)

- **Hay 19 mapas y 91 etapas, verificados**: 10 ucronías, 8 de extensión acumulada y 1 de prospectiva con 38 casos. La auditoría da 0 errores y es reproducible byte a byte. El README y el `manifest` de la app están desfasados.
- **Hallazgo clave: `atlas-escenarios/dist` no sirve como fuente.** Su generador simplifica todas las geometrías (Gran Alemania pasa de 46 386 a 10 349 vértices y Fráncfort cambia un 29 % de área), descarta las 24 entidades de contexto de 1848 y aplana categorías y tramas de leyenda. Se migra desde los originales vectoriales: el GeoJSON incrustado en `europa_1848.html` y `mapas/*/datos/escenario.geojson`. Los mapas que solo existen como generador (6 ucronías y 8 de extensión) se regeneran sin simplificar sobre las mismas capas HB, fijadas por hash.
- **Duplicados:** 12 grupos idénticos por hash (copias en `source-data/`, `dist/prospectiva/` y licencias). Ninguna variante aporta información que se pierda al quedarse con el original.
- **Material perdido:** el mapa japonés original de ChatGPT, la vista centroeuropea de 1848, los zip, el SVG y el PNG de 1848, `ww1-interactivo.html` y el emblema. No se buscó fuera de `Mapas/` (P1). El despliegue anterior se ha descargado: es un atlas de historia real 1783–1945 con su módulo de la Primera Guerra Mundial, no el de 1848. Es candidato a una fase opcional.
- **Arquitectura propuesta:** `atlas/index.html` autónomo, Leaflet local y datos `atlas/data/<id>.js` cargados bajo demanda con un contrato v2: geometrías únicas por `gid`, `kind` en cuatro clases, `category` como leyenda original, `role` que separa soberanía, control, ocupación, dependencia, influencia, reclamación, proyecto y caso, y `certainty` independiente de `precision`. Interfaz con la paleta `mapeo.cfg`; los colores de los datos no se tocan.
- **Fases:** contrato (Opus) → datos (Codex) y front (Opus) en paralelo → revisión histórica (Gemini) → integración (Opus) con aprobación de Marcos. La validación bloqueante es la igualdad de hashes de geometría entre el original y el atlas.
- **Pendiente de Marcos:** las decisiones P1 a P9. Hasta su visto bueno no se implementa nada.

# Tareas del atlas

Lo mantiene el orquestador. Cada rol actualiza solo el estado de sus tareas.
Estados: `pendiente` · `en curso` · `bloqueada` · `en revisión` · `hecha`.
Contexto y criterios: `PLAN.md` (las secciones se citan como §). Formato de datos: `CONTRATO.md`. Prompts para lanzar cada rol: `PROMPTS.md`.

| # | Tarea | Rol | Estado | Rama / worktree | Notas |
|---|---|---|---|---|---|
| 0 | Inventario y plan (`PLAN.md`, `INVENTARIO.csv`) | Orquestador | hecha | main | Aprobada por Marcos y publicada (commit 1b624ce) |
| 1 | Contrato de datos front ↔ datos (v2, §5.2) y `atlas/data/_ejemplo.js` | Orquestador | hecha | main | `CONTRATO.md`, `data/_ejemplo.js` + `data/_catalogo-ejemplo.js` (generados por `_tmp/generar_ejemplo.py`) y `PROMPTS.md`. P1–P9 provisionales (§9). Sin commit: lo gestiona Marcos |
| 2.1 | Copiar originales a `atlas/source-data/originales/` + `MANIFEST.csv` con sha256, verificado (§6.1) | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `build/congelar_originales.py`: 41 ficheros (18 MB) con hash verificado en `source-data/originales/MANIFEST.csv`. Incluye `mapa-datos.js` de la prospectiva |
| 2.2 | `atlas/source-data/BASES.csv` (HB/NE: URL, commit, sha256) + script de descarga con comprobación (§6.2) | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main (segunda entrega), sin worktree. `source-data/BASES.csv`: 23 capas HB fijadas al commit `4b5039e` y 4 de Natural Earth al `ca96624` (v5.1.2), con sha256 y blob git; los commits se han localizado comparando los blobs. `build/descargar_bases.py` descarga y verifica (las 27 coinciden). Solo se copian las 20 capas HB que lee el generador (30 MB en `source-data/bases/hb/`); `admin_1` de 40 MB, solo hash (P7) |
| 2.3 | Portar los generadores a `atlas/build/` + prueba de equivalencia con `TOLERANCE=.018` frente a `dist/` (§6.3–6.4) | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main (segunda entrega), sin worktree. Port en `build/hb/` (`v1_datos.py`, `v1_extension.py`, `extension_complementos.py` y `comun.py`): solo cambian las rutas, la tolerancia (`ATLAS_TOLERANCE`) y que no escribe ficheros. `build/hb/equivalencia.py`: con `.018` reproduce los 19 escenarios de `dist/` con JSON idéntico (3168 geometrías) y `land.js`. Sin simplificar, `make_valid` solo si hace falta (0 reparaciones) |
| 2.4 | Gran Alemania, Carlos, Centrales y Eje a resolución completa, con `category`, colores, tramas y las 24 `context` de 1848 | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main (segunda entrega), sin worktree. Completadas las etapas que faltaban: Centrales 1914/1918, Eje 1938 y la capa del Sacro Imperio de Carlos. Roles provisionales hasta R2 |
| 2.5 | Ucronías derivadas de HB (japon, gran-colombia, kalmar, mexico-norte, centroamerica, tres-naciones) sin simplificar | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main (segunda entrega), sin worktree. japon, gran-colombia, kalmar, mexico-norte, centroamerica y tres-naciones, sin simplificar. Leyenda por role, como en el visor anterior |
| 2.6 | Los 8 mapas `max-*` (`kind: extension`, `start`/`end`/`lost`) sin simplificar | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main (segunda entrega), sin worktree. Los 8 `max-*` con `start`/`end`/`lost`/`period` y `roleNames`; category = periodo o corona de su leyenda (`p0`…). Recuentos por etapa iguales a `dist/` |
| 2.7 | Prospectiva `fronteras-2101`: `kind: prospective`, `role: case`, `category` = `level` | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `fronteras-2101`: 4 etapas, 38 casos, `role: case`, `category` = `level` |
| 2.8 | Validador: hash canónico por geometría, recuentos, puntos, leyendas, `MANIFEST.json` (§8) | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main (segunda entrega), sin worktree. `build/validar.py` cubre los 19 mapas: 1027 geometrías por hash canónico (originales congelados o generador portado re-ejecutado), hashes de `BASES.csv`, recuentos por etapa frente al generador y frente a `atlas-escenarios/dist` (18 mapas; Gran Alemania difiere a propósito), vocabularios y leyendas |
| 2.9 | `atlas/CREDITS.md` y `license` por fuente (HB GPL-3.0, NE, HistoGIS/IEG, Leaflet) | Datos (Codex) | en curso | atlas-datos | Primera versión de `atlas/CREDITS.md`. Falta verificar la licencia de HistoGIS/HGIS |
| 3.1 | Estructura de `atlas/index.html` con la paleta `mapeo.cfg` (copia de `PALETTES` + test de igualdad), tipografías y portada por `kind` (§5.3–5.4) | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `atlas/index.html` sustituye la página provisional (que pasa a `plan.html`, con plan, tareas, contrato y créditos). `test/paleta.cjs` comprueba que `PALETTES` es igual |
| 3.2 | Visor Leaflet local (`atlas/vendor/leaflet/`), carga bajo demanda, `#/<id>/<año>`, encuadres `views` | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. Leaflet 1.9.4 en `vendor/leaflet/` (hashes como en el inventario), carga bajo demanda, `#/<id>/<año>`, encuadres |
| 3.3 | Leyenda por `category`, tramas, fichas, roles, fuentes y licencias | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. Leyenda filtrable por `category`, tramas originales, ficha con role, certainty y precision separados, fuentes y licencias |
| 3.4 | Línea del tiempo discreta y teclado (←/→, Inicio/Fin), sin interpolar | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. Etapas pendientes deshabilitadas con su motivo |
| 3.5 | Distinción visible de `kind`; «acumulado, no simultáneo»; avisos de la prospectiva | Front (Opus) | hecha | atlas-front | Primera entrega, más en la segunda: extensión acumulada con «acumulado, no simultáneo», `lost` atenuado, intensidad del dominio (`roleNames`), años de posesión en la ficha y años a. C. |
| 3.6 | Móvil (390 × 844), foco visible y `prefers-reduced-motion` | Front (Opus) | hecha | atlas-front | `test/navegador.cjs`: 19 mapas y sus 84 etapas sin errores de consola, teclado, paleta clara, ficha de extensión, años a. C. y móvil a 390 × 844 (136 comprobaciones) |
| R1 | Clases `kind` y etapas `historical` (P2) | Revisión (Gemini) | pendiente | solo lectura → `atlas/revision/` | Desbloqueada (2.4–2.7 hechas) |
| R2 | Tablas `category → role` por mapa (soberanía, control, ocupación, dependencia, influencia, reclamación, proyecto) | Revisión (Gemini) | hecha | solo lectura → `atlas/revision/` | Informe de Gemini en `atlas/revision/R2-roles.md` (25-11-2026): 31 cambios propuestos, 10 bloqueantes, 13 recomendables y 8 menores. Integración pendiente (F11) |
| R3 | Extensión acumulada: omisiones, fechas `start`/`end`, `lost` | Revisión (Gemini) | pendiente | solo lectura → `atlas/revision/` | Desbloqueada (2.6 hecha) |
| R4 | Redacción y avisos de la prospectiva 2101 | Revisión (Gemini) | pendiente | solo lectura → `atlas/revision/` | Desbloqueada (2.7 hecha) |
| 5 | Integración de ramas, validación del §8 y petición de aprobación a Marcos | Orquestador | bloqueada | main | Sin push a `main` sin aprobación explícita |
| 6 | (Opcional) Historia real 1783–1945 a partir del despliegue anterior, regenerada desde HB en lon/lat | Datos + Front | bloqueada | — | Solo si Marcos lo decide (P8) |

## Peticiones entre roles

<!-- Un rol que necesite un cambio en ficheros de otro lo pide aquí. -->

## Dudas de la primera entrega (decididas de forma conservadora)

- **E1.** Datos y front los ha hecho el orquestador en `main`, sin pasar por los worktrees `atlas-datos` y `atlas-front`, porque Marcos pidió algo visible cuanto antes. Los hilos de rol parten de este estado: `PROMPTS.md` sigue valiendo, pero hay que decirles qué está hecho.
- **E2.** En Centrales y en el Eje solo se migran las etapas que salen del original (1920/1925 y 1942–1948). Las de referencia (1914, 1918 y 1938) dependen de capas HB y aparecen como «pendientes» en la línea del tiempo. No se han copiado desde `dist/` porque allí están simplificadas.
- **E3.** A Carlos le falta la capa «Sacro Imperio · estados con gobierno propio», que `build_data.py` calcula a partir de HB 1600. Las tramas de frontera del mapa mundial (`frontier`) las calcula `generar.py` y no están en `escenario.geojson`, así que tampoco se han migrado. Ambas cosas se avisan en los límites del mapa.
- **E4.** En Gran Alemania aparecen las 24 entidades de contexto en las tres etapas, como en el único estado del original. En la v1 no aparecían.
- **E5.** La leyenda de Centrales agrupa categorías por color, igual que la original. La tabla de agrupación (en `build/migrar_originales.py`) es explícita y tendrá que revisarla R2.
- **E6.** El Eje dibuja tres categorías que no tienen entrada en su leyenda original (`neutral`, `britain` y `russia`). Se han añadido al final con la etiqueta «sin entrada en la leyenda original».
- **E7.** La tierra neutra de fondo es la base de Natural Earth que ya usa la prospectiva (`mapa-datos.js`), sin fronteras. No es un dato histórico.
- **E8.** La descarga GeoJSON agrupa por entidad, con `years` y `certaintyByYear`, en lugar de repetir la geometría en cada etapa (la de Gran Alemania pasaba de 3 a 8,5 MB).
- **E9.** Se ha cambiado una frase de la tarjeta del atlas en `typemaps/index.html` («En construcción: de momento, el plan y las tareas»), porque ya no era cierta. No se ha tocado nada más fuera de `atlas/`.
- **E10.** `source-data/originales/` (18 MB, con PNG de render) se publicaría con el sitio (P6). No se ha creado `.vercelignore`.
- **E11.** La prueba del navegador usa Chrome sin interfaz con un perfil temporal en `atlas/_tmp/perfil-navegador/`, que se borra al terminar.

## Dudas de la segunda entrega (decididas de forma conservadora)

- **F1.** Las etapas y mapas que salen de historical-basemaps no tienen otro «original» que el generador de `atlas-escenarios`. Por eso su origen es ese generador portado, ejecutado sin `simplify`: el validador vuelve a ejecutarlo y compara hashes. Sus textos, colores y roles son los de v1.
- **F2.** Sin simplificar, las piezas calculadas no cambian de forma salvo por la generalización que ya hacía el generador (recortes, uniones y fronteras de 1994 como guía). `precision` es `generalized` en las áreas y `approximate` en los puntos.
- **F3.** Las seis ucronías HB no tenían leyenda por categorías: el visor anterior mostraba los roles («Cómo leer este mapa»). Se usa eso como leyenda: `category` = `role`, sin color de muestra porque cada entidad tiene el suyo.
- **F4.** En la extensión acumulada, `category` es el periodo (o la corona en `max-iberia`) con las claves `p0`, `p1`…, y el role se muestra aparte como «intensidad del dominio», con las etiquetas `roleNames` del generador. Las relaciones débiles se dibujan más claras y la soberanía nominal con trazo discontinuo, como en v1.
- **F5.** Las capas de referencia de Centrales 1914 y Eje 1938 llevan los colores que les dio v1, no los del mapa original (que no tenía esas etapas). Su entrada de leyenda va marcada «sin entrada en la leyenda original».
- **F6.** El Sacro Imperio de Carlos es la capa de v1 (HB 1600 menos los territorios del escenario), rellena con `#d8ccaa`. El `generar.py` original solo dibujaba un contorno discontinuo de otra unión. Se usa la entrada «Sacro Imperio · vínculo institucional» de la leyenda original.
- **F7.** Los puertos y rutas de las ucronías HB usan los colores del visor anterior (`app.js`).
- **F8.** Las capas HB copiadas en `source-data/bases/` (30 MB) también se publicarían con el sitio (como E10). Si Marcos prefiere no publicarlas, bastan `BASES.csv` y `descargar_bases.py` con un `.vercelignore`.
- **F9.** `world_1500`, `world_1920` y `world_1945` solo se registran en `BASES.csv` (no las lee el generador portado). Las capas de Natural Earth tampoco se copian: el atlas usa la salida del generador de la prospectiva.
- **F10.** R2 se ha delegado en Gemini en segundo plano. Hasta que se integre su informe, los roles siguen marcados como provisionales en la ficha y en `MANIFEST.json`.
- **F11.** El informe R2 ya está entregado, pero no se ha aplicado: cambiar roles (por ejemplo `core` de 1848 a `federal`) o quitar entradas del generador (la pieza «Poland» de `max-otomano`) es una decisión de contenido. Queda para que el orquestador revise el informe con Marcos y lo lleve a las tablas `category → role` de `build/`. Mientras tanto, los roles siguen marcados como provisionales.

## Preguntas abiertas para Marcos

Ver `PLAN.md` §9 (P1–P10, adoptadas como **provisionales** con la opción conservadora) y `CONTRATO.md` §13 (dudas C1–C6 del contrato). Marcos las revisará; mientras tanto, rige lo provisional.

# Tareas del atlas

Lo mantiene el orquestador. Cada rol actualiza solo el estado de sus tareas.
Estados: `pendiente` · `en curso` · `bloqueada` · `en revisión` · `hecha`.
Contexto y criterios: `PLAN.md` (las secciones se citan como §). Formato de datos: `CONTRATO.md`. Prompts para lanzar cada rol: `PROMPTS.md`.

| # | Tarea | Rol | Estado | Rama / worktree | Notas |
|---|---|---|---|---|---|
| 0 | Inventario y plan (`PLAN.md`, `INVENTARIO.csv`) | Orquestador | hecha | main | Aprobada por Marcos y publicada (commit 1b624ce) |
| 1 | Contrato de datos front ↔ datos (v2, §5.2) y `atlas/data/_ejemplo.js` | Orquestador | hecha | main | `CONTRATO.md`, `data/_ejemplo.js` + `data/_catalogo-ejemplo.js` (generados por `_tmp/generar_ejemplo.py`) y `PROMPTS.md`. P1–P9 provisionales (§9). Sin commit: lo gestiona Marcos |
| 2.1 | Copiar originales a `atlas/source-data/originales/` + `MANIFEST.csv` con sha256, verificado (§6.1) | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `build/congelar_originales.py`: 41 ficheros (18 MB) con hash verificado en `source-data/originales/MANIFEST.csv`. Incluye `mapa-datos.js` de la prospectiva |
| 2.2 | `atlas/source-data/BASES.csv` (HB/NE: URL, commit, sha256) + script de descarga con comprobación (§6.2) | Datos (Codex) | pendiente | atlas-datos | Desbloqueada. Averiguar el commit de HB; `admin_1` de 40 MB solo con hash (P7) |
| 2.3 | Portar los generadores a `atlas/build/` + prueba de equivalencia con `TOLERANCE=.018` frente a `dist/` (§6.3–6.4) | Datos (Codex) | pendiente | atlas-datos | Desbloqueada. Para las etapas que dependen de HB: centrales 1914/1918, eje 1938 y el Sacro Imperio de Carlos |
| 2.4 | Gran Alemania, Carlos, Centrales y Eje a resolución completa, con `category`, colores, tramas y las 24 `context` de 1848 | Datos (Codex) | en curso | atlas-datos | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `build/migrar_originales.py`: Gran Alemania completa (3 etapas, 91 entidades con las 24 `context`), Carlos (4 etapas, sin el Sacro Imperio), Centrales 1920/1925 y Eje 1942/1944/1948. Falta lo que depende de HB (ver 2.3). Roles provisionales (regla v1) hasta R2 |
| 2.5 | Ucronías derivadas de HB (japon, gran-colombia, kalmar, mexico-norte, centroamerica, tres-naciones) sin simplificar | Datos (Codex) | bloqueada | atlas-datos | Depende de 2.3 |
| 2.6 | Los 8 mapas `max-*` (`kind: extension`, `start`/`end`/`lost`) sin simplificar | Datos (Codex) | bloqueada | atlas-datos | Depende de 2.3. Los parches de `extension_complementos.py` se mantienen |
| 2.7 | Prospectiva `fronteras-2101`: `kind: prospective`, `role: case`, `category` = `level` | Datos (Codex) | hecha | atlas-datos | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `fronteras-2101`: 4 etapas, 38 casos, `role: case`, `category` = `level` |
| 2.8 | Validador: hash canónico por geometría, recuentos, puntos, leyendas, `MANIFEST.json` (§8) | Datos (Codex) | en curso | atlas-datos | Primera versión `build/validar.py`: re-extrae las 376 geometrías de los originales congelados y compara el hash canónico; 0 errores; escribe `data/MANIFEST.json`. Falta cubrir los mapas de 2.5 y 2.6 |
| 2.9 | `atlas/CREDITS.md` y `license` por fuente (HB GPL-3.0, NE, HistoGIS/IEG, Leaflet) | Datos (Codex) | en curso | atlas-datos | Primera versión de `atlas/CREDITS.md`. Falta verificar la licencia de HistoGIS/HGIS |
| 3.1 | Estructura de `atlas/index.html` con la paleta `mapeo.cfg` (copia de `PALETTES` + test de igualdad), tipografías y portada por `kind` (§5.3–5.4) | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `atlas/index.html` sustituye la página provisional (que pasa a `plan.html`, con plan, tareas, contrato y créditos). `test/paleta.cjs` comprueba que `PALETTES` es igual |
| 3.2 | Visor Leaflet local (`atlas/vendor/leaflet/`), carga bajo demanda, `#/<id>/<año>`, encuadres `views` | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. Leaflet 1.9.4 en `vendor/leaflet/` (hashes como en el inventario), carga bajo demanda, `#/<id>/<año>`, encuadres |
| 3.3 | Leyenda por `category`, tramas, fichas, roles, fuentes y licencias | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. Leyenda filtrable por `category`, tramas originales, ficha con role, certainty y precision separados, fuentes y licencias |
| 3.4 | Línea del tiempo discreta y teclado (←/→, Inicio/Fin), sin interpolar | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. Etapas pendientes deshabilitadas con su motivo |
| 3.5 | Distinción visible de `kind`; «acumulado, no simultáneo»; avisos de la prospectiva | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. Textos de `CONTRATO.md` §8.1. El texto de la extensión acumulada aún no se ha visto en pantalla porque no hay mapas `extension` |
| 3.6 | Móvil (390 × 844), foco visible y `prefers-reduced-motion` | Front (Opus) | hecha | atlas-front | Hecha por el orquestador en main a petición de Marcos (primera entrega), sin worktree. `test/navegador.cjs`: los 5 mapas y sus 16 etapas sin errores de consola, teclado, paleta clara y móvil a 390 × 844; capturas en `test/capturas/` |
| R1 | Clases `kind` y etapas `historical` (P2) | Revisión (Gemini) | bloqueada | solo lectura → `atlas/revision/` | Depende de 2.4–2.7 |
| R2 | Tablas `category → role` por mapa (soberanía, control, ocupación, dependencia, influencia, reclamación, proyecto) | Revisión (Gemini) | pendiente | solo lectura → `atlas/revision/` | Desbloqueada (2.1 hecha): trabaja sobre las copias de `source-data/originales/` |
| R3 | Extensión acumulada: omisiones, fechas `start`/`end`, `lost` | Revisión (Gemini) | bloqueada | solo lectura → `atlas/revision/` | Depende de 2.6 |
| R4 | Redacción y avisos de la prospectiva 2101 | Revisión (Gemini) | bloqueada | solo lectura → `atlas/revision/` | Depende de 2.7 |
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

## Preguntas abiertas para Marcos

Ver `PLAN.md` §9 (P1–P10, adoptadas como **provisionales** con la opción conservadora) y `CONTRATO.md` §13 (dudas C1–C6 del contrato). Marcos las revisará; mientras tanto, rige lo provisional.

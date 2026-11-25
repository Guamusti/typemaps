# Tareas del atlas

Lo mantiene el orquestador. Cada rol actualiza solo el estado de sus tareas.
Estados: `pendiente` · `en curso` · `bloqueada` · `en revisión` · `hecha`.
Contexto y criterios: `PLAN.md` (las secciones se citan como §).

| # | Tarea | Rol | Estado | Rama / worktree | Notas |
|---|---|---|---|---|---|
| 0 | Inventario y plan (`PLAN.md`, `INVENTARIO.csv`) | Orquestador | hecha | main | Solo lectura. Espera el visto bueno de Marcos |
| 1 | Contrato de datos front ↔ datos (v2, §5.2) y `atlas/data/_ejemplo.js` | Orquestador | bloqueada | main | Espera el visto bueno de Marcos y las respuestas a P1–P9 (§9) |
| 2.1 | Copiar originales a `atlas/source-data/originales/` + `MANIFEST.csv` con sha256, verificado (§6.1) | Datos (Codex) | bloqueada | atlas-datos | Ni chats ni `.libs` ni `hosting.json`. Puede empezar con la fase 0 aprobada |
| 2.2 | `atlas/source-data/BASES.csv` (HB/NE: URL, commit, sha256) + script de descarga con comprobación (§6.2) | Datos (Codex) | bloqueada | atlas-datos | Averiguar el commit de HB; `admin_1` de 40 MB solo con hash (P7) |
| 2.3 | Portar los generadores a `atlas/build/` + prueba de equivalencia con `TOLERANCE=.018` frente a `dist/` (§6.3–6.4) | Datos (Codex) | bloqueada | atlas-datos | Depende de 1 y 2.1. No ejecutar `refine_ui.cjs` ni `finish_ui.cjs` |
| 2.4 | Gran Alemania, Carlos, Centrales y Eje a resolución completa, con `category`, colores, tramas y las 24 `context` de 1848 | Datos (Codex) | bloqueada | atlas-datos | Depende de 2.3 y R2 |
| 2.5 | Ucronías derivadas de HB (japon, gran-colombia, kalmar, mexico-norte, centroamerica, tres-naciones) sin simplificar | Datos (Codex) | bloqueada | atlas-datos | Depende de 2.3 |
| 2.6 | Los 8 mapas `max-*` (`kind: extension`, `start`/`end`/`lost`) sin simplificar | Datos (Codex) | bloqueada | atlas-datos | Depende de 2.3. Los parches de `extension_complementos.py` se mantienen |
| 2.7 | Prospectiva `fronteras-2101`: `kind: prospective`, `role: case`, `category` = `level` | Datos (Codex) | bloqueada | atlas-datos | Depende de 1 |
| 2.8 | Validador: hash canónico por geometría, recuentos, puntos, leyendas, `MANIFEST.json` (§8) | Datos (Codex) | bloqueada | atlas-datos | Bloquea la integración |
| 2.9 | `atlas/CREDITS.md` y `license` por fuente (HB GPL-3.0, NE, HistoGIS/IEG, Leaflet) | Datos (Codex) | bloqueada | atlas-datos | — |
| 3.1 | Estructura de `atlas/index.html` con la paleta `mapeo.cfg` (copia de `PALETTES` + test de igualdad), tipografías y portada por `kind` (§5.3–5.4) | Front (Opus) | bloqueada | atlas-front | Depende de 1 |
| 3.2 | Visor Leaflet local (`atlas/vendor/leaflet/`), carga bajo demanda, `#/<id>/<año>`, encuadres `views` | Front (Opus) | bloqueada | atlas-front | Trabaja con `_ejemplo.js` |
| 3.3 | Leyenda por `category`, tramas, fichas, roles, fuentes y licencias | Front (Opus) | bloqueada | atlas-front | Los colores de los datos no se repintan |
| 3.4 | Línea del tiempo discreta y teclado (←/→, Inicio/Fin), sin interpolar | Front (Opus) | bloqueada | atlas-front | — |
| 3.5 | Distinción visible de `kind`; «acumulado, no simultáneo»; avisos de la prospectiva | Front (Opus) | bloqueada | atlas-front | — |
| 3.6 | Móvil (390 × 844), foco visible y `prefers-reduced-motion` | Front (Opus) | bloqueada | atlas-front | — |
| R1 | Clases `kind` y etapas `historical` (P2) | Revisión (Gemini) | bloqueada | solo lectura → `atlas/revision/` | Depende de 2.4–2.7 |
| R2 | Tablas `category → role` por mapa (soberanía, control, ocupación, dependencia, influencia, reclamación, proyecto) | Revisión (Gemini) | bloqueada | solo lectura → `atlas/revision/` | Se puede empezar sobre los originales tras 2.1 |
| R3 | Extensión acumulada: omisiones, fechas `start`/`end`, `lost` | Revisión (Gemini) | bloqueada | solo lectura → `atlas/revision/` | Depende de 2.6 |
| R4 | Redacción y avisos de la prospectiva 2101 | Revisión (Gemini) | bloqueada | solo lectura → `atlas/revision/` | Depende de 2.7 |
| 5 | Integración de ramas, validación del §8 y petición de aprobación a Marcos | Orquestador | bloqueada | main | Sin push a `main` sin aprobación explícita |
| 6 | (Opcional) Historia real 1783–1945 a partir del despliegue anterior, regenerada desde HB en lon/lat | Datos + Front | bloqueada | — | Solo si Marcos lo decide (P8) |

## Peticiones entre roles

<!-- Un rol que necesite un cambio en ficheros de otro lo pide aquí. -->

## Preguntas abiertas para Marcos

Ver `PLAN.md` §9 (P1–P9). Mientras no se respondan, se aplica la opción conservadora indicada allí.

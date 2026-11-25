# typemaps — instrucciones para agentes

Sitio estático con juegos de mecanografía y geografía: https://typemaps.vercel.app (repo `Guamusti/typemaps`).
Interfaz y textos en **español**. El dueño es Marcos: responde siempre en español.

## Estructura

- `index.html` — portada con una tarjeta por sección.
- `tecleo/` — test de mecanografía (un solo `index.html`).
- `mapeo/` — mapas: `index.html` (app principal), `juegos.html` (minijuegos), `reto.html`, `banderas.html`.
  Los datos son scripts `.js` que asignan a `window.*` (`data.js`, `hist/eYYYY.js`, `sil/XX.js`, `geo.js`…) y se cargan bajo demanda.
- `ondeo/` — solo redirige a `mapeo/banderas.html`.
- `atlas/` — **sección nueva** (cartografía histórica, ucronías y prospectiva). Aún no existe; ver más abajo.

## Convenciones

- **Sin compilación ni framework.** Cada página es un HTML autónomo con su CSS y JS dentro. Las dependencias de terceros se guardan en local (por ejemplo `atlas/vendor/leaflet/`), nunca desde un CDN en tiempo de ejecución.
- **Ligero:** los datos pesados se trocean en archivos que se cargan solo cuando hacen falta.
- **Paleta compartida:** los colores salen de variables CSS (`--bg`, `--alt`, `--text`, `--sub`, `--accent`, `--err`, `--land`, `--line`). La paleta elegida se guarda en `localStorage` en la clave `mapeo.cfg`. Las secciones nuevas deben leerla y respetarla.
- **Tipografía:** Instrument Serif para titulares y JetBrains Mono para el texto.
- **Accesible y fluida:** se maneja con teclado, respeta `prefers-reduced-motion` y no tiene animaciones costosas (nada de `filter: blur` animado, por ejemplo).
- **Comentarios:** en inglés, breves y explicando el porqué.
- **Créditos y licencias:** cada fuente de datos se anota en el `CREDITS.md` de su sección.

## Despliegue — importante

**Hacer push a `main` publica el sitio** (Vercel lo despliega automáticamente). Por eso:
- No hagas `git push` ni merges a `main` sin que Marcos lo apruebe explícitamente.
- Trabaja en ramas o en worktrees. Commits pequeños, con mensajes en español.
- No toques las secciones existentes (`tecleo/`, `mapeo/`) salvo para añadir el enlace a `atlas/` en `index.html` cuando se pida.

## Sección `atlas/` (en preparación)

Su objetivo es unificar los proyectos de `C:\00. Marcos\02. Personal\Mapas` (la app `atlas-escenarios` y los mapas sueltos de `mapas\`) en `typemaps/atlas/`.

Reglas que no se negocian:
- **Conservar** las fronteras, subdivisiones, colores y significado de las leyendas originales. Unificar el motor no puede suponer cambiar geometrías por aproximaciones.
- **Distinguir siempre** entre historia real, contrafactual o ucronía, prospectiva y extensión imperial acumulada. La certeza documental (`documented`/`scenario`) no es lo mismo que la precisión geométrica.
- **No interpolar** fronteras entre años, **no inventar** superficies a partir de marcadores y **no vectorizar PNG** si existe una fuente vectorial.
- **Antes de transformar nada,** copiar los originales a `atlas/source-data/originales/` y registrar su hash SHA-256.
- No editar a mano las salidas generadas: se modifica el generador.
- `atlas-escenarios` tiene un registro de hosting privado en `.openai/hosting.json`: no lo modifiques ni lo publiques.
- No ejecutar `scripts/refine_ui.cjs` ni `scripts/finish_ui.cjs` de `atlas-escenarios`.

## Roles y coordinación (T3 Code)

El trabajo del atlas se reparte entre un orquestador y tres subagentes, cada uno con un modelo fijo:

| Rol | Modelo | Dónde trabaja | Es dueño de |
|---|---|---|---|
| Orquestador | Opus | `main` (checkout actual) | `atlas/PLAN.md`, `atlas/TAREAS.md`, el contrato de datos, la integración |
| Front | **solo Opus** | worktree propio | `atlas/index.html` y el CSS/JS de la interfaz |
| Datos y geometrías | Codex | worktree propio | `atlas/data/`, `atlas/build/`, `atlas/source-data/` |
| Revisión histórica | Gemini (Antigravity) | solo lectura | informes en `atlas/revision/` |

Flujo:
1. El orquestador define primero el **contrato de datos** (formato de los ficheros que el front consume) y lo deja en `PLAN.md`.
2. Front y datos trabajan en paralelo, cada uno en su rama o worktree, sin tocar ficheros del otro.
3. La revisión histórica lee lo que producen los datos y escribe sus observaciones en `atlas/revision/`; no edita nada más.
4. El orquestador revisa, integra las ramas y pide a Marcos aprobación antes de cualquier push a `main`.

Coordinación:
- Se coordina a través de ficheros del repo: `PLAN.md` (qué y por qué), `TAREAS.md` (quién hace qué y en qué estado) y `atlas/revision/`.
- `delegate_task` o mencionar un modelo con @ solo para tareas cortas y acotadas.
- Si una tarea necesita tocar ficheros de otro rol, se anota en `TAREAS.md` en lugar de editarlos.

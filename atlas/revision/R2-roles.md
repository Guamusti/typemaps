# Revisión histórica R2 — Tablas `category → role`

Fecha: 25-11-2026 · Rol: Revisión histórica (solo lectura) · Alcance: los 18 mapas históricos, contrafactuales y de extensión acumulada de `atlas/data/`.  
Excluido: `fronteras-2101` (`kind: prospective`, usa `role: case`).

---

## Criterios metodológicos de la revisión

1. **Separación de planos (`kind` y `certainty`):**
   - **Historia real** (`historical: true` / `documented`): etapas de referencia de 1848 (`gran-alemania`), 1914 (`centrales`), 1938 (`eje`, `japon`), 1822 (`mexico-norte`), 1824 (`centroamerica`), 1650 (`tres-naciones`), 1819/1822 (`gran-colombia`) y 1520 (`kalmar`).
   - **Ucronía** (`counterfactual`): etapas posteriores a la divergencia (`scenario`). Un `role` correcto debe distinguir soberanía reconocida (`sovereign`), miembro confederal o federal (`federal`), control de hecho sin reconocimiento (`control`), ocupación militar o administración colonial de ocupación (`occupation`), Estado satélite, vasallo o protectorado (`dependent`), esfera de influencia (`influence`), reclamación o vínculo dinástico discutido (`claim`) y plan no ejecutado (`project`).
   - **Extensión acumulada** (`extension`): territorios gobernados, protegidos, ocupados o reclamados **en algún momento**, nunca simultáneos. En los 8 `max-*`, `category` representa el periodo de incorporación (`p0`, `p1`…) o corona (`max-iberia`), mientras que `role` expresa la intensidad del dominio con etiquetas propias en `roleNames`.
   - **Certeza documental frente a precisión geométrica:** el `role` evalúa la relación jurídica o de poder representada en cada etapa, no la exactitud del trazo (`precision`). Las anomalías de geometría o recorte observadas se recogen como **observaciones aparte** sin proponer ediciones manuales.

2. **Origen de los errores detectados:**
   - En `gran-alemania`, `carlos`, `centrales` y `eje`, la función provisional `normalize()` / `role_v1()` de `build_data.py` y `migrar_originales.py` no contemplaba los roles `federal`, `control` ni `project` introducidos en `CONTRATO.md` §8.2, y volcaba por defecto a `sovereign` o `claim`.
   - En las ucronías derivadas de `historical-basemaps` (`japon`, `gran-colombia`, `kalmar`, `mexico-norte`, `centroamerica`, `tres-naciones`) y en los 8 `max-*`, el `role` fue fijado manualmente por el generador; allí aparecen inconsistencias puntuales (mandatos de la Sociedad de Naciones repartidos entre `sovereign` y `dependent`, `project` ausente, o falsos positivos automáticos en `max-otomano`).

---

## 1. Ucronías con original cartográfico propio (4 mapas)

### 1.1 `gran-alemania` — La solución granalemana (1848★, 1849, 1851)

En 1848★ el mapa describe el *Deutscher Bund* (Confederación Germánica); en 1849 y 1851, la unión constitucional granalemana. Tratar `core`, `east` y `exception` como `sovereign` borra la diferencia entre los miembros confederales/federales y los Estados vecinos de `context` (duda `C1` de `CONTRATO.md`).

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| gran-alemania | `core` (44 entidades: 36 Estados alemanes y 8 tierras confederales austríacas) | `sovereign` | `federal` | bloqueante | Miembros de la Confederación Germánica en 1848★ y de la unión constitucional en 1849–1851; encajan literalmente en `federal` («Miembro de una federación o confederación») y se distinguen de `context`. | https://www.hgisg-ekompendium.ieg-mainz.de/Dokumentation_Datensaetze/Multimedia/Staatenwelten/Deutscher_Bund.php |
| gran-alemania | `east` (`Prusia Oriental`, `Prusia Occidental`, 1849–1851) | `sovereign` | `federal` | bloqueante | Provincias prusianas admitidas en el Bund el 11-04-1848 e incorporadas al territorio federal del proyecto de Fráncfort en el escenario. | https://www.verfassungen.de/de06-66/bundesakte15.htm |
| gran-alemania | `exception` (`Holstein`, `Lauenburg`, `Luxemburgo`, `Limburgo`) | `sovereign` | `federal` | bloqueante | Miembros confederales con estatuto excepcional por unión personal con Dinamarca o Países Bajos; participaban en la Dieta y en Fráncfort como miembros del Bund. | https://www.hgisg-ekompendium.ieg-mainz.de/Dokumentation_Datensaetze/Multimedia/Sonstige_Gebiete/Limburg.php |
| gran-alemania | `diaspora` (`Transilvania`, 1851) | `claim` | `claim` | — (sin cambio) | Fuera del Bund; región con minoría sajona invocada en debates nacionalistas pero sin pertenencia confederal. | https://www.dhm.de/mediathek/die-nationalversammlung-in-der-paulskirche-1848/details-und-debatten/item/showDetail/Topic/?tx_dhm_topic%5BcategoryItem%5D=6416 |
| gran-alemania | `dynasty` (6 entidades habsbúrgicas fuera del Bund, 1851) | `claim` | `claim` | — (sin cambio) | Posesiones de los Habsburgo fuera del Bund (`Galicia y Lodomeria`, `Bucovina`, `Dalmacia`, `Croacia civil`, `Eslavonia civil`, `Frontera Militar`); vinculadas al proyecto *Großösterreich* por vínculo dinástico (`claim`). | https://mrp.oeaw.ac.at/pages/show.html?directory=editions&document=MRP-1-2-01-0-00000000-einleitung.xml |
| gran-alemania | `conflict` (`Hungría`, `Lombardía–Véneto`, 1851) | `claim` | `claim` | — (sin cambio) | Posesiones dinásticas habsbúrgicas en ruptura constitucional (Leyes de Abril húngaras) o guerra revolucionaria en 1848; zonas disputadas respecto a cualquier incorporación. | https://histogis.acdh.oeaw.ac.at/shapes/shapes/?in_between=1848-05-18 |
| gran-alemania | `uncertain` (`Posen · provincia con admisión parcial`, `Litoral · Görz–Gradisca e Istria`, `Galicia occidental · excepción Auschwitz–Zator`, `Schleswig`) | `claim` | `claim` | — (sin cambio) | Zonas mixtas, particiones parciales (22-04/02-05-1848), excepciones jurídicas de límites sin verificar o territorios reclamados (`Schleswig`, §1 Constitución de 1849). | https://www.bundestag.de/resource/blob/940964/1853fa82d8e80d8fd80f6233ab1886a5/booklet_constitution_1849.pdf |
| gran-alemania | `uncertain` (`Maastricht`, `Venlo`, `Alsacia–Lorena francesa`) | `claim` | `sovereign` | bloqueante | Error claro: los propios atributos del original precisan que `Maastricht` y `Venlo` estaban explícitamente excluidas del Bund bajo soberanía neerlandesa, y `Alsacia–Lorena` bajo soberanía francesa sin proyecto confederal consensuado. | https://www.hgisg-ekompendium.ieg-mainz.de/Dokumentation_Datensaetze/Multimedia/Sonstige_Gebiete/Limburg.php |
| gran-alemania | `uncertain` (`Neuchâtel`) | `claim` | `sovereign` | menor | Proclamada república dentro de la Confederación Suiza el 01-03-1848 y fuera del Bund; se anota duda frente a `claim` por la pretensión dinástica prusiana mantenida hasta el Tratado de París de 1857. | https://histogis.acdh.oeaw.ac.at/shapes/source/detail/166 |
| gran-alemania | `context` (20 Estados soberanos vecinos) | `sovereign` | `sovereign` | — (sin cambio) | Estados europeos externos al Bund (Francia, Reino Unido, Imperio ruso, España, etc.); resuelve la duda `C1` al quedar diferenciados de los `federal`. | https://histogis.acdh.oeaw.ac.at/shapes/source/detail/166 |
| gran-alemania | `context` (`Malta`, `Gibraltar`, `Islas Jónicas`, `Polonia del Congreso`) | `sovereign` | `dependent` | menor | Excepciones dentro de `context`: en 1848 `Malta` y `Gibraltar` eran colonias británicas, `Islas Jónicas` un protectorado británico (1815–1864) y `Polonia del Congreso` un reino subordinado al Imperio ruso tras 1832. | https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/other-countries/ |

**Duda anotada (`gran-alemania`):** en `dynasty`, si se quisiera enfatizar en 1851 el plan no realizado de Schwarzenberg (*Großösterreich*), podría valorarse `project`, pero dado que la ficha describe su condición real en 1848–1851 como «vínculo dinástico, sin título confederal», `claim` se ajusta mejor a `CONTRATO.md` §8.2 («Reclamaciones, vínculos dinásticos, zonas discutidas»). Asimismo, en `context`, si el generador asigna un solo `role` por `category`, mantener `sovereign` para toda la categoría es aceptable dejando las 4 excepciones documentadas en `note`.

---

### 1.2 `carlos` — La herencia de Carlos (1556, 1580, 1600, 1640)

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| carlos | `hisp` (Coronas hispánicas, Milán, Nápoles, Sicilia, Cerdeña) | `sovereign` | `sovereign` | — (sin cambio) | Núcleos dinásticos bajo soberanía directa del monarca común (Milán como feudo investido pero gobernado por la rama hispánica). | https://germanhistorydocs.org/en/from-the-reformations-to-the-thirty-years-war-1500-1648/the-abdication-of-emperor-charles-v-1555-56 |
| carlos | `port` (`Reino de Portugal`, desde 1580) | `sovereign` | `sovereign` | — (sin cambio) | En el escenario, Portugal se integra en pie de igualdad dinástica dentro de la monarquía común compartida, conservando sus leyes e instituciones. | https://ejercito.defensa.gob.es/museo/HECHOS_HISTORICOS/HECHOS_HISTORICOS/08.25_BATALLA_DE_ALCANTARA.html |
| carlos | `burg` (`Países Bajos reunificados`, `Franco Condado`) | `sovereign` | `sovereign` | — (sin cambio) | Herencia borgoñona conservada bajo soberanía común mediante el acuerdo político supuesto por la ucronía. | https://www.nationaalarchief.nl/beleven/onderwijs/bronnenbox/plakkaat-van-verlatinge-1581 |
| carlos | `aust`, `bohem`, `royal` (Tierras austríacas, Bohemia, Hungría Real) | `sovereign` | `sovereign` | — (sin cambio) | Dominios patrimoniales y coronas de la rama austríaca unidos al pacto sucesorio común del escenario. | https://www.habsburger.net/en/chapter/birth-austrian-line-ferdinand-i |
| carlos | `imperial` (`Sacro Imperio · estados con gobierno propio`) | `influence` | `influence` | — (sin cambio) | Dignidad imperial electiva con vínculo institucional, no posesión directa ni soberanía de la Monarquía sobre los principados y ciudades imperiales. | https://www.habsburger.net/en/glossary/holy-roman-empire |
| carlos | `escolon`, `ptcolon` (implantación colonial americana, Filipinas, franja de Brasil) | `sovereign` | `sovereign` | — (sin cambio) | Representan los núcleos virreinales, ejes andinos y franjas costeras de implantación colonial efectiva (diferenciados en el original de la capa `frontier`). | https://asia.si.edu/whats-on/exhibitions/encompassing-the-globe-portugal-and-the-world-in-the-16th-and-17th-centuries/ |

**Observación y duda (`carlos`):** la capa de tramas `frontier` de `mapas/monarquia-universal/generar.py` (*Frontera septentrional novohispana*, *Perú · horizonte jurisdiccional interior*, *Brasil · hinterland reclamado*) aún no está migrada en `carlos.js` (`TAREAS.md` E3); cuando se incorpore, deberá asignársele `role: claim`. En cuanto a `escolon` y `ptcolon`, existe la duda de si la presencia colonial discontinua frente a pueblos indígenas autónomos en partes de Nueva España merece `control` o `sovereign`; se mantiene `sovereign` por coherencia con la separación ya hecha en el original entre núcleos (`escolon`/`ptcolon`) y horizontes reclamados (`frontier`).

---

### 1.3 `centrales` — Victoria de las Potencias Centrales (1914★, 1918, 1920, 1925)

En `centrales`, `normalize()` falló al asignar `sovereign` a `Estado vinculado a Alemania — hipótesis` y a `Dobruja: reparto pendiente`.

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| centrales | `ref1914` (Estados soberanos de 1914★) | `sovereign` | `sovereign` | — (sin cambio) | Capa de referencia real de 1914 para Estados independientes (Alemania, Austria-Hungría, Francia, Rusia, Reino Unido, etc.). | https://github.com/aourednik/historical-basemaps |
| centrales | `ref1914` y `Estado de referencia` (excepciones: `Grand Duchy of Finland`, `Tunisia`, `Morocco`, `Spanish Morocco`, `Egypt`, `Kuwait`, `Malta`, `Libya`, `Algeria`, `Iceland`) | `sovereign` | `dependent` | menor | En 1914 eran autonomías imperiales (Finlandia en Rusia, Islandia en Dinamarca), protectorados (Túnez, Marruecos, Kuwait, Egipto desde dic. 1914) o colonias (Malta, Libia, Argelia). | https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/other-countries/ |
| centrales | `Potencia central` (Alemania, Austria-Hungría, Imperio otomano, Bulgaria) | `sovereign` | `sovereign` | — (sin cambio) | Potencias soberanas vencedoras del escenario contrafactual (1920–1925). | https://www.dhm.de/lemo/kapitel/erster-weltkrieg/innenpolitik/septemberprogramm |
| centrales | `Anexión propuesta` (`Luxembourg`, 1920–1925) | `sovereign` | `sovereign` | — (sin cambio) | En el escenario de 1920 la anexión prevista en el *Septemberprogramm* se da por consumada dentro del Reich (históricamente fue solo ocupación militar en 1914–1918 y proyecto). | https://www.dhm.de/lemo/kapitel/erster-weltkrieg/innenpolitik/septemberprogramm |
| centrales | `Ampliación búlgara — hipótesis` (`Macedonia del Vardar`) | `sovereign` | `sovereign` | — (sin cambio) | Transferencia territorial incorporada a Bulgaria en el escenario hipotético de posguerra. | https://history.state.gov/historicaldocuments/frus1917Supp02v01/d404 |
| centrales | `Reparto de 1918 simplificado` (`Dobruja: reparto pendiente`) | `sovereign` | `occupation` | recomendable | En el Tratado de Bucarest (07-05-1918), solo Dobruja meridional pasó a Bulgaria; el norte quedó bajo condominio/ocupación conjunta de las Potencias Centrales pendiente de reparto. | https://library.law.fsu.edu/Digital-Collections/LimitsinSeas/pdf/ibs053.pdf |
| centrales | `Estado vinculado a Alemania — hipótesis` (`Ducado Báltico`, `Lituania`, `Polonia`, `Ucrania`, 1918–1925) | `sovereign` | `dependent` | bloqueante | Error de `normalize()`: las cuatro entidades representan Estados satélites/clientes proyectados tras Brest-Litovsk bajo tutela militar, dinástica y económica de Alemania (`Ober Ost` / *Mitteleuropa*). | https://avalon.law.yale.edu/20th_century/bl34.asp |
| centrales | `Estado vinculado a Alemania — hipótesis` (`Finlandia`, 1918–1925) | `sovereign` | `influence` | recomendable | `generar.py` aclara que Finlandia se interpreta como «aliada vinculada a Alemania», no como territorio anexionado ni ocupación plena; en 1918 estuvo bajo fuerte esfera de influencia política, militar y comercial alemana. | https://history.state.gov/historicaldocuments/frus1919Parisv12/d66 |
| centrales | `Soberanía restringida — hipótesis` (`Bélgica`, `Montenegro`, `Serbia`, `Rumanía`) | `dependent` | `dependent` | — (sin cambio) | Estados vencidos supervivientes pero sometidos a servidumbres militares y económicas (como el Tratado de Bucarest o el programa alemán sobre Bélgica). | https://www.dhm.de/lemo/kapitel/erster-weltkrieg/innenpolitik/septemberprogramm |
| centrales | `Zona de negociación` (Bélgica/Briey, frontera polaco-rusa, rectificaciones carpáticas) | `claim` | `claim` | — (sin cambio) | Trama `hatch` que señala reclamaciones o fronteras abiertas sin adjudicación cerrada. | https://www.dhm.de/lemo/kapitel/erster-weltkrieg/innenpolitik/septemberprogramm |
| centrales | `Estado de referencia` (Estados soberanos en 1920–1925) | `sovereign` | `sovereign` | — (sin cambio) | Estados neutrales o ex-aliados de referencia (Francia, Reino Unido, Italia, Rusia, España, etc.). | https://github.com/aourednik/historical-basemaps |

**Observación de geometría/datos (`centrales`):** en 1920 y 1925 persisten en `Estado de referencia` dos artefactos de la capa HB 1914: `Grand Duchy of Finland` (en el sector ruso-finlandés tras el recorte) y `Territorio sin identificar` (que según `PLAN.md` §3.3 tiene un 46 % de diferencia de área en `dist`).

---

### 1.4 `eje` — Victoria del Eje en Europa (1938★, 1942, 1944, 1948)

En `eje`, el fallo más grave de `normalize()` es asignar `claim` a los 7 territorios con `project: true` (trama `project`) y `sovereign` a `Transnistria · administración rumana` y a las anexiones bélicas unilaterales de hecho.

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| eje | `ref1938` (Estados soberanos de 1938★) | `sovereign` | `sovereign` | — (sin cambio) | Capa de referencia de 1938 para Estados independientes (Alemania —incluye Austria—, Reino Unido, Francia, Italia, URSS, etc.). | https://github.com/aourednik/historical-basemaps |
| eje | `ref1938` y `neutral` (mandatos/protectorados/colonias: `Mandatory Palestine`, `Syria`, `Jordan`, `Tunisia`, `Morocco`, `Algeria`, `Libya`, `British Raj`, `Egypt`, `Mesopotamia`) | `sovereign` | `dependent` | menor | En 1938 eran mandatos de la Sociedad de Naciones, protectorados o posesiones coloniales británicas, francesas o italianas, no Estados soberanos (Irak era formalmente independiente desde 1932 pero bajo tratado de alianza/influencia británica). | https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/other-countries/ |
| eje | `reich` (`Reich alemán`) | `sovereign` | `sovereign` | — (sin cambio) | Núcleo estatal alemán de partida (base 1938). | https://encyclopedia.ushmm.org/content/en/map/german-administration-of-europe-1942 |
| eje | `reich` (`Luxemburgo`, `Alsacia y Mosela · incorporación de hecho`, `Memel · incorporación al Reich`, `Territorios polacos incorporados al Reich`, `Eslovenia septentrional`) | `sovereign` | `control` | recomendable | Anexiones unilaterales de hecho durante la ocupación sin tratado de paz ni reconocimiento internacional (el propio catálogo advierte: «el color expresa control, no legitimidad»); Memel fue cedida por Lituania bajo ultimátum en 1939. | https://encyclopedia.ushmm.org/content/en/map/german-administration-of-europe-1942 |
| eje | `occupation` (`Bélgica`, `Países Bajos`, `Noruega`, `Dinamarca`, `Protectorado de Bohemia y Moravia`, `Gobierno General`, `Serbia`) | `occupation` | `occupation` | — (sin cambio) | Administraciones militares o civiles alemanas de ocupación (`Militärverwaltung`, `Reichskommissariat`, `Generalgouvernement`, `Reichsprotektorat`). Matiz: Dinamarca mantuvo gobierno propio tutelado hasta agosto de 1943. | https://encyclopedia.ushmm.org/content/en/map/german-administration-of-europe-1942 |
| eje | `east` sin `project` (`Ostland · administración alemana`, `Ucrania · administración alemana`) | `occupation` | `occupation` | — (sin cambio) | *Reichskommissariate* civiles de administración colonial y ocupación establecidos desde 1941. | https://avalon.law.yale.edu/imt/1997-ps.asp |
| eje | `east` con `project: true` (`Moscovia*`, `Cáucaso*`, `Crimea*`, 1944–1948) | `claim` | `project` | bloqueante | Error de `normalize()` al no existir `project` en v1: son planes de administración oriental no llegados a establecerse (`Reichskommissariat Moskowien`, `Kaukasien`, proyecto colonial de Crimea). | https://www.dhm.de/lemo/kapitel/der-zweite-weltkrieg/voelkermord/generalplan-ost |
| eje | `ally` / `italian` con `project: true` (`Carelia oriental*`, `Córcega*`, `Túnez*`, `Niza*`, 1944–1948) | `claim` | `project` | bloqueante | En el original llevan `pattern: "project"` («expansión proyectada, no realizada»); unificarlos en `project` alinea la trama con `CONTRATO.md` §8.2, anotando su componente irredentista/reivindicativo. | https://encyclopedia.ushmm.org/content/en/article/italy |
| eje | `italy` (`Italia`, `Libia italiana`) | `sovereign` | `sovereign` | — (sin cambio) | Metrópoli italiana y colonia libia integrada administrativamente en 1939 (*Quarta Sponda*, aunque sin derechos para la población colonizada). | https://encyclopedia.ushmm.org/content/en/article/italy |
| eje | `italy` (`Eslovenia meridional`, `Dalmacia: enclaves y costa italianos`) | `sovereign` | `control` | recomendable | Anexiones unilaterales de guerra tras la invasión de Yugoslavia de abril de 1941 (Provincia de Liubliana y Gobernación de Dalmacia), sin reconocimiento internacional. | https://encyclopedia.ushmm.org/content/en/article/axis-invasion-of-yugoslavia |
| eje | `italian` sin `project` (`Albania ampliada bajo Italia`) | `dependent` | `dependent` | — (sin cambio) | Reino satélite en unión personal con la Corona italiana desde 1939, ampliado en 1941 con Kosovo y Macedonia occidental. | https://encyclopedia.ushmm.org/content/en/article/axis-invasion-of-yugoslavia |
| eje | `italian` sin `project` (`Grecia`, `Montenegro · tutela italiana`) | `dependent` | `occupation` | recomendable | Ocupación militar italiana/del Eje en Grecia (1941–1943, con gobierno colaboracionista) y gobernación militar en Montenegro tras fracasar la monarquía satélite. | https://encyclopedia.ushmm.org/content/en/article/axis-invasion-of-yugoslavia |
| eje | `ally` sin `project` (`Bulgaria`, `Rumanía`, `Hungría`, `Finlandia`, `Dobruja meridional`, `Transilvania septentrional`) | `sovereign` | `sovereign` | — (sin cambio) | Estados soberanos aliados o cobeligerantes del Eje, más cesiones formalizadas en 1940 (Craiova y Segundo Arbitraje de Viena). | https://encyclopedia.ushmm.org/content/en/map/german-administration-of-europe-1942 |
| eje | `ally` sin `project` (`Rutenia subcarpática`, `Bačka y Baranja`, `Macedonia del Vardar`, `Tracia y Macedonia oriental`) | `sovereign` | `control` | recomendable | Incorporaciones y administraciones unilaterales de guerra (1939 y 1941) tras el desmembramiento de Checoslovaquia, Yugoslavia y Grecia, sin tratado general de paz. | https://encyclopedia.ushmm.org/content/en/article/axis-invasion-of-yugoslavia |
| eje | `ally` sin `project` (`Transnistria · administración rumana`) | `sovereign` | `occupation` | bloqueante | Contradice la propia ficha («Ocupación administrativa no equivale a anexión reconocida»): la Gobernación de Transnistria (1941–1944) fue una zona de ocupación administrada por Rumanía, nunca anexionada. | https://encyclopedia.ushmm.org/content/en/map/german-administration-of-europe-1942 |
| eje | `client` (`Francia`, `Eslovaquia`, `Croacia y Bosnia · Estado dependiente`, `Yugoslavia: reparto posterior`) | `dependent` | `dependent` | — (sin cambio) | Regímenes satélites o subordinados al Eje (Vichy, Eslovaquia, NDH ustacha); en Francia convivió con ocupación directa alemana/italiana. | https://encyclopedia.ushmm.org/content/en/article/axis-invasion-of-yugoslavia |
| eje | `neutral` (Estados soberanos), `britain`, `russia` | `sovereign` | `sovereign` | — (sin cambio) | Estados independientes fuera del Eje (Reino Unido tras paz negociada en la ucronía, espacio soviético residual, España, Suiza, Suecia, Turquía, Portugal, Irlanda). | https://github.com/aourednik/historical-basemaps |

**Observación de geometría/datos (`eje`):** (1) En `client`, `Yugoslavia: reparto posterior` aparece en 1942–1948 como residuo geométrico de HB 1938 tras sustraer los territorios repartidos en 1941, no como entidad política real; (2) en `ref1938` y `neutral`, `Armenia` (anomalía sobredimensionada de HB 1938 en el Cáucaso/Anatolia oriental que el propio `victoria-eje/generar.py` corrige para Turquía) y `Hejaz` (ya integrado en Arabia Saudí desde 1932) son residuos de la capa HB 1938; (3) si en la ucronía de 1948 se interpretara que la paz negociada convalida las anexiones de hecho (`reich`, `italy`, `ally`), podrían mantenerse en `sovereign` solo en 1948 y `control` en 1942–1944; se recomienda `control` en todas las etapas alternativas para no legitimar anexiones bélicas sin tratado explícito.

---

## 2. Ucronías derivadas de `historical-basemaps` (6 mapas)

En estos seis mapas, `category` replica directamente el `role` fijado a mano en `build_data.py` y `build_extension.py`.

### 2.1 `japon` — Victoria japonesa en Asia-Pacífico (1938★, 1940, 1943, 1948)

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| japon | `sovereign` (`Imperio japonés · territorio imperial`, `Tailandia · aliada de Japón`) | `sovereign` | `sovereign` | — (sin cambio) | Metrópoli japonesa y posesiones imperiales integradas en 1938 (Corea, Taiwán) más Tailandia como reino aliado con gobierno propio. | https://www.jacar.go.jp/english/exhibition/showa100/01_03.html |
| japon | `dependent` (`Manchukuo`, `Gobierno de Nankín`, `Filipinas`, `Birmania`, `Indonesia · independencia tutelada`) | `dependent` | `dependent` | — (sin cambio) | Regímenes satélites o tutelados bajo predominio militar y económico japonés (la promesa de independencia indonesia solo aparece en 1948). | https://www.jacar.archives.go.jp/das/meta-en/C14020058100 |
| japon | `occupation` (`Indochina`, `Malaya y Borneo británico`, `Indias Orientales Neerlandesas` en 1943) | `occupation` | `occupation` | — (sin cambio) | Administraciones militares de ocupación o tutela directa sobre colonias europeas (en Indochina coexistió con la administración de Vichy hasta marzo de 1945). | https://history.state.gov/historicaldocuments/frus1943CairoTehran/d231 |
| japon | `influence` (`China · hegemonía japonesa disputada`, 1948) | `influence` | `influence` | — (sin cambio) | Hegemonía y concesiones forzadas sin ocupación homogénea del interior chino ni disolución de las resistencias. | https://history.state.gov/historicaldocuments/frus1943CairoTehran/d231 |

### 2.2 `gran-colombia` — La Gran Colombia federal (1819, 1822, 1830, 1850)

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| gran-colombia | `sovereign` (1819, 1822: `Nueva Granada`, `Venezuela`, `Quito`, `Istmo de Panamá`) | `sovereign` | `sovereign` | — (sin cambio) | Etapas previas a la divergencia federal de 1830: la República de Colombia (Ley de Angostura de 1819 y Constitución de Cúcuta de 1821) era unitaria/centralista. | https://enciclopedia.banrepcultural.org/index.php?title=El_proyecto_grancolombiano |
| gran-colombia | `federal` (1830, 1850: los cuatro componentes) | `federal` | `federal` | — (sin cambio) | Pacto federal de la ucronía desde 1830 con autonomía regional entre Nueva Granada, Venezuela, Quito e Istmo de Panamá. | https://babel.banrepcultural.org/digital/collection/p17054coll26/id/5985/ |

**Observación menor (`gran-colombia`):** en 1819 y 1822 las entidades ya llevan en su `name` el sufijo `· componente federal`, lo que anticipa la reforma de 1830; además, en 1819 la guerra de independencia seguía abierta en Venezuela, Quito y el Caribe neogranadino (antes de Carabobo 1821 y Pichincha 1822), como ya advierte el texto de la etapa.

### 2.3 `kalmar` — La Unión de Kalmar perdura (1520, 1523, 1536, 1600)

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| kalmar | `sovereign` (1520★, 1523: `Dinamarca y Noruega · coronas vinculadas`, `Suecia y Finlandia · corona sueca`) | `sovereign` | `sovereign` | — (sin cambio) | Reinos soberanos en unión personal dinástica en crisis antes del pacto institucional. | https://lex.dk/tidslinje_over_Kalmarunionen%2C_1397-1523 |
| kalmar | `sovereign` (1536, 1600: ambas entidades en la unión renegociada) | `sovereign` | `federal` | recomendable | Desde 1536 el escenario supone un consejo común confederal pactado que limita la primacía danesa sin abolir las leyes de cada reino; homologable al criterio de `federal` usado en `tres-naciones` y `gran-colombia`. | https://lex.dk/Kalmarunionen |

**Duda anotada (`kalmar`):** si `federal` en `CONTRATO.md` §8.2 se reserva a federaciones/confederaciones con carta constitucional o tratado de unión real explícito (como Lublin 1569 o Centroamérica 1824) y se excluyen las uniones personales dinásticas, `sovereign` puede mantenerse en las cuatro etapas siempre que se aclare en la ficha; el cambio a `federal` desde 1536 refleja mejor la divergencia política descrita en el texto («consejo común pactado»).

### 2.4 `mexico-norte` — México conserva su norte (1822★, 1836, 1848, 1880)

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| mexico-norte | `sovereign` (`México` 1822–1880, `Estados Unidos` 1822–1880, `Texas` 1822) | `sovereign` | `sovereign` | — (sin cambio) | Estados soberanos y núcleo centralista del Primer Imperio mexicano en 1822 (anterior a la Constitución federal de 1824). | https://avalon.law.yale.edu/19th_century/sp1819.asp |
| mexico-norte | `federal` (`Texas` 1836–1880, `Alta California y Nuevo México` 1848–1880) | `federal` | `federal` | — (sin cambio) | Estados federados dentro de la República mexicana según la hipótesis del escenario. | https://www.tshaonline.org/handbook/entries/texas-revolution |
| mexico-norte | `claim` (`Alta California y Nuevo México`, 1822–1836) | `claim` | `claim` | — (sin cambio) | Título jurídico heredado del Tratado Adams-Onís (1819), pero con presencia dispersa y amplias zonas bajo control efectivo de pueblos indígenas independientes (comanches, apaches, navajos). | https://avalon.law.yale.edu/19th_century/sp1819.asp |
| mexico-norte | `dependent` (`Centroamérica`, 1822★) | `dependent` | `occupation` | menor | En enero de 1822 las provincias centroamericanas se anexionaron al Imperio Mexicano de Iturbide (no eran un protectorado separado), y El Salvador resistió militarmente siendo ocupado por tropas imperiales en 1823 antes de la separación de julio de 1823. | https://www.britannica.com/place/United-Provinces-of-Central-America |

### 2.5 `centroamerica` — Centroamérica unida (1824★, 1838, 1860, 1914)

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| centroamerica | `federal` (Guatemala, El Salvador, Honduras, Nicaragua, Costa Rica; Los Altos desde 1838) | `federal` | `federal` | — (sin cambio) | Estados miembros de la República Federal de Centroamérica (Constitución de 1824 y reforma del escenario de 1838). | https://www.britannica.com/place/United-Provinces-of-Central-America |
| centroamerica | `dependent` (`Reino misquito`, 1824–1838) | `dependent` | `dependent` | — (sin cambio) | Protectorado británico en la costa caribeña hasta el Tratado de Managua (1860), reintegrado en la etapa de 1860 del escenario. | https://avalon.law.yale.edu/19th_century/br1850.asp |
| centroamerica | `claim` (`Belice británico`, 1824–1914) | `claim` | `claim` | — (sin cambio) | Asentamiento británico sin soberanía plena en 1824–1838 y territorio reclamado por Guatemala/Federación; nota: desde 1862 el Reino Unido lo administró formalmente como colonia de Honduras Británica (`control`/`sovereign` británico frente a `claim` federal). | https://avalon.law.yale.edu/19th_century/br1850.asp |

### 2.6 `tres-naciones` — La Mancomunidad de las Tres Naciones (1650★, 1658, 1667, 1700)

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| tres-naciones | `federal` (`Corona del Reino de Polonia`, `Gran Ducado de Lituania`, `Gran Ducado de Rutenia` desde 1658) | `federal` | `federal` | — (sin cambio) | Unión real confederal de la Mancomunidad (Unión de Lublin de 1569) y tercer miembro proyectado por el Tratado de Hadiach (1658). | https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CH%5CA%5CHadiachTreatyof1658.htm |
| tres-naciones | `sovereign` (`Zarato de Moscovia`) | `sovereign` | `sovereign` | — (sin cambio) | Estado soberano vecino de referencia. | https://www.britannica.com/event/Truce-of-Andrusovo |

---

## 3. Mapas de extensión acumulada (8 mapas `max-*`)

En los ocho mapas `extension`, `category` indica el periodo histórico de incorporación (`p0`–`p5`, o la corona en `max-iberia`) y `role` describe la «intensidad del dominio». Siguiendo la pauta de R2, se resume la coherencia global de cada mapa y se listan únicamente las entradas con errores o matices claros.

### 3.1 `max-espana` — Todo lo que fue español (1479 – 1976)

- **Resumen:** de 70 entradas (periodos `p0`–`p5`), la clasificación general distingue correctamente los núcleos peninsulares, italianos y virreinales (`sovereign`), los presidios norteafricanos breves y enclaves puntuales (`influence`), las fronteras abiertas sin control efectivo (`claim`: *Septentrión novohispano*, *Patagonia y Araucanía*, *Belice*, *Pacífico noroeste*), los protectorados del siglo XX (`dependent`: *Protectorado de Marruecos*, *Cabo Juby*) y las intervenciones militares (`occupation`: *Blavet*, *Cochinchina*, *Tánger*).
- **Duda anotada (Unión Ibérica 1580–1640, 15 entradas en `p1`):** todas las posesiones portuguesas durante la unión de coronas (`Reino de Portugal`, `Brasil portugués`, `Goa`, `Malaca`, `Macao`, `Luanda`, `Ormuz`, `Madeira`, `Azores`, `Cabo Verde`, `Santo Tomé`, `Guinea portuguesa`, `Mozambique`, `Mombasa`, `Ceilán`) llevan `dependent` («Vasallaje o protectorado»). Históricamente fue una unión dinástica *aeque principaliter* bajo el mismo soberano, no un vasallaje a Castilla; se mantiene `dependent` por claridad visual en este mapa acumulado, anotando la naturaleza dinástica del vínculo.

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| max-espana | `p3`/`p4` (`Fernando Poo y Annobón` 1778–1968; `Ifni` 1860–1969) | `sovereign` | `claim` | menor | Las propias notas aclaran que la ocupación efectiva comenzó en 1843 (Fernando Poo) y 1934 (Ifni); entre la cesión nominal (El Pardo 1777/1778; Wad-Ras 1860) y la ocupación efectiva fueron títulos nominales (`claim`), aunque el periodo posterior sí fue `sovereign`. | https://dbe.rah.es/ |

**Observación de fechas (`max-espana`):** `Banda Oriental` (`p2`, `sovereign`) tiene `start: 1680`; en 1680 quien fundó Colonia del Sacramento fue Portugal, mientras que la fundación española de Montevideo data de 1724–1726 y la cesión definitiva de Colonia de 1777.

---

### 3.2 `max-portugal` — Todo lo que fue portugués (1415 – 1999)

- **Resumen:** de 48 entradas (`p0`–`p4`), separa bien el reino metropolitano, archipiélagos atlánticos y colonias de poblamiento (`sovereign`), los enclaves de la red marítima africana y asiática (`influence`), el litoral ceilandés y Fernando Poo sin control interior (`claim`), Zanzíbar (`dependent`) y la ocupación napoleónica de Guayana Francesa (`occupation`).

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| max-portugal | `p1` (`Macao`, 1557–1999) | `sovereign` | `influence` | recomendable | Hasta 1849 y el Tratado de Pekín de 1887 Macao fue un establecimiento comercial autorizado/arrendado bajo soberanía china (pagando foro), como ya señala el mapa `carlos`; solo desde fines del XIX tuvo estatuto colonial pleno. | https://asia.si.edu/whats-on/exhibitions/encompassing-the-globe-portugal-and-the-world-in-the-16th-and-17th-centuries/ |

**Observación menor (`max-portugal`):** existe cierta heterogeneidad en `p0`/`p1` entre plazas fuertes de larga duración etiquetadas como `sovereign` (`Tánger` 1471–1661, `Malaca` 1511–1641) y otras equivalentes en duración o estatuto etiquetadas como `influence` (`Mazagán` 1502–1769, `Ormuz` 1515–1622, `Cochín` 1503–1663).

---

### 3.3 `max-iberia` — Los dos imperios ibéricos (1415 – 1999)

- **Resumen:** superpone las entradas de `max-espana` (`p0`) y `max-portugal` (`p1`) conservando sus roles originales. Hereda las observaciones de `max-portugal` (`Macao`) y `max-espana` (`Fernando Poo`/`Ifni`).
- **Observación de datos (no cambio de role):** el filtro de `build_extension.py` línea 284 (`e['start'] == 1580`) no excluyó las tres entradas añadidas en `extension_complementos.py` con fecha de inicio posterior (`Azores · unión dinástica` 1583, `Guinea portuguesa · Cacheu` 1588 y `Mombasa · unión dinástica` 1593), por lo que aparecen duplicadas bajo `p0` (`dependent`) junto a las entradas portuguesas de `p1`.

---

### 3.4 `max-britanico` — Todo lo que fue británico (1541 – 1997)

- **Resumen:** de 81 entradas (`p0`–`p5`), distingue con rigor colonias y dominios (`sovereign`), protectorados, condominios y la mayoría de mandatos (`dependent`), ocupaciones bélicas (`occupation`: *La Habana*, *Manila*, *Buenos Aires*, *Islandia*, *Eritrea*, *Libia*, *Zona británica de Alemania*), esferas de influencia (*Afganistán*, *Omán*) y la *Reserva india de Ohio* (`claim`). Sin embargo, dos mandatos de la Sociedad de Naciones quedaron con `sovereign` por omisión en `build_extension.py`.

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| max-britanico | `p5` (`Tanganica` 1919–1961, `Camerún británico` 1916–1961) | `sovereign` | `dependent` | recomendable | Ambos fueron mandatos clase B de la Sociedad de Naciones (y luego fideicomisos ONU), no colonias bajo soberanía directa británica; en el mismo mapa `Camerún septentrional británico`, `Togoland británico`, `Palestina`, `Irak`, `Transjordania`, `África del Sudoeste`, `Nueva Guinea`, `Nauru` y `Samoa Occidental` sí llevan `dependent`. | https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/other-countries/ |

**Observación menor (`max-britanico`):** `Georgia del Sur` (`p2`, 1775–hoy) y `Malvinas` (`p3`, 1833–hoy) figuran como `sovereign` aunque sus notas advierten que la soberanía es disputada por Argentina; además, 1775 corresponde al avistamiento de Cook, mientras que la administración permanente británica de Georgia del Sur (como dependencia de las Malvinas) comenzó en 1908. `Weihaiwei` (`p4`, 1898–1930) fue territorio arrendado en China, análogo a `Guangzhouwan` en `max-frances`.

---

### 3.5 `max-frances` — Todo lo que fue francés (1534 – 1980)

- **Resumen:** de 51 entradas (`p0`–`p4`), separa bien metrópoli y colonias (`sovereign`), campañas y ocupaciones (`occupation`: *Santo Domingo*, *Egipto*, *España*, *Rusia*, *México*, *Fezán*, *Zona francesa de Alemania*), protectorados (`dependent`: *Túnez*, *Marruecos*, *Nuevas Hébridas*, *Siria y Líbano*), *Luisiana* (`claim`) y factorías breves o esferas (`influence`). Presenta la misma inconsistencia con dos mandatos africanos de la Sociedad de Naciones y un matiz en la *Confederación del Rin*.

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| max-frances | `p4` (`Togo` 1916–1960, `Camerún` 1916–1960) | `sovereign` | `dependent` | recomendable | Mandatos clase B de la Sociedad de Naciones (1922) y luego fideicomisos de la ONU, no territorios anexionados en soberanía plena (a diferencia de `Siria y Líbano`, que sí llevan `dependent` en el mismo mapa). | https://recherche-anom.culture.gouv.fr/ |
| max-frances | `p1` (`Confederación del Rin`, 1806–1813) | `influence` | `dependent` | menor | En los `max-*`, `influence` tiene la etiqueta «Enclave o presencia breve»; la Confederación del Rin fue un protectorado formal de estados clientes de Napoleón (`dependent`), análogo a `Italia napoleónica` y `Ducado de Varsovia`. | https://www.napoleon.org/ |

---

### 3.6 `max-roma` — Todo lo que fue romano (264 a. C. – 1453)

- **Resumen:** de 27 entradas (`p0`–`p4`), no se detectan errores claros de `role`. Separa adecuadamente las provincias consolidadas (`sovereign`), el reino cliente del `Bósforo cimerio` (`dependent`), las ocupaciones efímeras o fronterizas (`occupation`: *Germania Magna*, *Armenia*, *Mesopotamia y Asiria*, *Escocia antonina*) y `Crimea bizantina` (`influence`, evitando atribuir dominio directo sobre toda la estepa crimea recortada del contorno moderno).
- **Observación menor (`max-roma`):** en `Hispania` se advierte en la nota la reincorporación bizantina del sureste (Spania, 552–624), aunque `end` marca 409; no afecta al `role` (`sovereign`).

---

### 3.7 `max-mongol` — Todo lo que fue mongol (1206 – 1480)

- **Resumen:** de 27 entradas (`p0`–`p3`), distingue con acierto las conquistas integradas en el imperio y sus kanatos (`sovereign`), los reinos vasallos/tributarios (`dependent`: *Georgia y Armenia*, *Novgorod y Riazán*, *Bulgaria*, *Rum*, *Tíbet*, *Corea*), las campañas u ocupaciones efímeras o rechazadas (`occupation`: *Hungría*, *Polonia meridional*, *Dai Viet*, *Siria*, *Japón*, *Champa*, *Birmania*, *Java*, *Punyab*) y *Sajalín* (`influence`). Existe una incoherencia clara en `Rus de Kiev y estepa`.

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| max-mongol | `p1` (`Rus de Kiev y estepa`, 1240–1480) | `sovereign` | `dependent` | recomendable | La propia nota indica «Principados rusos tributarios de la Horda de Oro hasta 1480»; aunque la estepa póntico-caspia era dominio directo de la Horda de Oro (`sovereign`), los principados rusos del polígono (Vladímir, Moscú, Kiev) eran tributarios (`dependent`), igual que `Novgorod y Riazán`. | https://afe.easia.columbia.edu/mongols/ |

**Observación de geometría/fechas (`max-mongol`):** el polígono de `Rus de Kiev y estepa` incluye Bielorrusia y Ucrania hasta `end: 1480`, aunque el Gran Ducado de Lituania absorbió esas tierras occidentales ya en el siglo XIV.

---

### 3.8 `max-otomano` — Todo lo que fue otomano (1400 – 1922)

- **Resumen:** al generarse automáticamente por intersección de 13 capas HB (1400–1914) sobre países de 1994 más `OTTO_EXTRA`, la mayoría de las provincias balcánicas y de Oriente Medio (`sovereign`), los principados tributarios, Crimea y regencias berberiscas (`dependent`), `Otranto` (`occupation`) y `Aceh` (`influence`) son correctos, pero el algoritmo automático introduce varios falsos positivos y errores claros de `role`.

| mapa | category (o entidad) | role actual | role propuesto | gravedad | justificación | fuente |
|---|---|---|---|---|---|---|
| max-otomano | `p1` (`Poland`, 1530–1650) | `sovereign` | `— (retirar; falso positivo)` | bloqueante | Error claro: Polonia-Lituania nunca estuvo bajo soberanía otomana en 1530–1650 (la única posesión otomana fue `Podolia` entre 1672 y 1699, ya incluida aparte en `OTTO_EXTRA`). Proviene de una intersección residual entre capas HB de 1530–1650 y Polonia 1994. | https://www.britannica.com/place/Ottoman-Empire |
| max-otomano | `p4` (`Chad`, 1880–1900) | `sovereign` | `claim` | bloqueante | El Imperio otomano nunca ejerció dominio soberano efectivo sobre Chad (solo reclamaciones transaharianas tardías desde Tripolitania/Fezán y guarniciones efímeras en Tibesti en 1911–1912). | https://www.britannica.com/place/Ottoman-Empire |
| max-otomano | `p1` (`Georgia`, 1492) | `sovereign` | `dependent` | recomendable | En 1492 los reinos y principados georgianos no eran provincias de administración directa otomana (sujetos a tributo/vasallaje intermitente en el XVI; Samtskhe no se convierte en eyalato de Çıldır hasta 1578). | https://www.britannica.com/place/Ottoman-Empire |
| max-otomano | `p2`/`p4` (`Eritrea`, `Habesh`, `Zeila`, 1650–1800 y 1880–1900) | `sovereign` | `dependent` | recomendable | El control otomano del Eyalato de Habesh fue costero y discontinuo; en el XIX (1865–1885) Massaua, Suakin y Zeila fueron transferidas al Jedivato autónomo de Egipto, igual que `Sudán` (que sí figura como `dependent`). | https://www.britannica.com/place/Ottoman-Empire |
| max-otomano | `p1` (`Kuwait`, 1530–1900) | `sovereign` | `dependent` | menor | Tras la presencia en Al-Hasa (XVI–XVII), el emirato de Kuwait funcionó desde el siglo XVIII con amplia autonomía local (nominalmente vinculado al vilayato de Basora) y desde 1899 bajo protectorado británico. | https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/other-countries/ |

**Observaciones de geometría/capas (`max-otomano`):** (1) `Rumanía` en `p0` y `p1` hereda `dependent` por la regla automática, lo que mezcla los principados tributarios (ya añadidos en `Valaquia` y `Moldavia`) con Dobruja (eyalato directo de Silistra, `sovereign`); (2) `Argelia` reaparece en `p4` (1880) aunque era colonia francesa desde 1830, y `Túnez` (protectorado francés desde 1881) y `Egipto` (ocupación británica desde 1882) figuran también en 1880 por reflejar HB 1880 suzeranías nominales; (3) `Yemen` aparece continuo 1530–1922 aunque fue perdido ante los imanes zaidíes entre 1635 y mediados del XIX.

---

## Resumen de cambios propuestos por gravedad

| Gravedad | N.º de filas de cambio | Detalle resumido |
|---|---|---|
| **Bloqueante** | **10** | `gran-alemania` (`core` → `federal`, `east` → `federal`, `exception` → `federal`, `Maastricht`/`Venlo`/`Alsacia–Lorena` → `sovereign`); `centrales` (`Estado vinculado a Alemania — hipótesis` [4 entidades] → `dependent`); `eje` (`east` con `project` → `project`, `ally`/`italian` con `project` → `project`, `Transnistria` → `occupation`); `max-otomano` (`Poland` falso positivo a retirar, `Chad` → `claim`). |
| **Recomendable** | **13** | `centrales` (`Dobruja: reparto pendiente` → `occupation`, `Finlandia` → `influence`); `eje` (`reich` anexiones de hecho → `control`, `italy` Eslovenia/Dalmacia → `control`, `italian` Grecia/Montenegro → `occupation`, `ally` ocupaciones/anexiones de guerra → `control`); `kalmar` (1536–1600 → `federal`); `max-portugal` (`Macao` → `influence`); `max-britanico` (`Tanganica`, `Camerún británico` → `dependent`); `max-frances` (`Togo`, `Camerún` → `dependent`); `max-mongol` (`Rus de Kiev y estepa` → `dependent`); `max-otomano` (`Georgia` 1492 → `dependent`, `Eritrea`/`Habesh`/`Zeila` → `dependent`). |
| **Menor** | **8** | `gran-alemania` (`Neuchâtel` → `sovereign` con duda anotada, 4 excepciones en `context` → `dependent`); `centrales` (excepciones HB 1914 en `ref1914`/`Estado de referencia` → `dependent`); `eje` (excepciones HB 1938 en `ref1938`/`neutral` → `dependent`); `mexico-norte` (`Centroamérica` 1822 → `occupation`); `max-espana` (`Fernando Poo` 1778–1843 e `Ifni` 1860–1934 → `claim`); `max-frances` (`Confederación del Rin` → `dependent`); `max-otomano` (`Kuwait` → `dependent`). |
| **Total cambios propuestos** | **31** | Sobre los **18 mapas** revisados (`fronteras-2101` excluido por usar `case`). |

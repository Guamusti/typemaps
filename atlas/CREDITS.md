# Créditos y licencias del atlas

Primera versión (25-11-2026), escrita con la primera entrega visible. La tarea 2.9 la completará y verificará. Las fuentes documentales de cada mapa aparecen en su ficha («Fuentes») y en `data/catalog.js`.

## Datos cartográficos

| Fuente | Uso en el atlas | Licencia |
|---|---|---|
| [historical-basemaps](https://github.com/aourednik/historical-basemaps) (A. Ourednik) | Base de la que derivan las geometrías de Carlos, Centrales y Eje (`mapas/*/datos/escenario.geojson`) y de los mapas calculados por el generador portado: las seis ucronías HB, los ocho de extensión acumulada, Centrales 1914/1918, Eje 1938 y el Sacro Imperio. Capas fijadas al commit `4b5039e` en `source-data/BASES.csv` | GPL-3.0. Los datos derivados se distribuyen con la misma licencia y se pueden descargar desde cada mapa («Descargar GeoJSON») |
| [HistoGIS](https://histogis.acdh.oeaw.ac.at/) (ACDH-CH, Academia Austríaca de Ciencias) y HGIS Germany | Geometrías del mapa de 1848 (`europa_1848.html`) | **Por verificar** (tarea 2.9) |
| [Natural Earth](https://www.naturalearthdata.com/) | Áreas de los casos de la prospectiva 2101 y tierra neutra de fondo (`data/land.js`) | Dominio público |

Las geometrías se publican tal como están en los originales de `Mapas/`, sin simplificar. Las copias congeladas y sus hashes están en `source-data/originales/MANIFEST.csv`.

## Programas

| Programa | Uso | Licencia |
|---|---|---|
| [Leaflet 1.9.4](https://leafletjs.com) | Visor de mapas (`vendor/leaflet/`, copia local) | BSD-2-Clause (`vendor/leaflet/LEAFLET-LICENSE.txt`) |
| Instrument Serif y JetBrains Mono (Google Fonts) | Tipografías, cargadas igual que en el resto de typemaps | SIL Open Font License 1.1 |

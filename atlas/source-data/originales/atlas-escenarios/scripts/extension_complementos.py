"""Revisión de omisiones, 6-11-2026. No modifica el frontend.

Los puntos localizan enclaves y archipiélagos sin atribuirles un interior ficticio.
Mandatos de los dominios se distinguen de las colonias administradas por Londres.
"""
def apply_review(b):
 if b.get('_review_applied'):return
 b['_review_applied']=True
 E,P,M,H,I,U,D,src=[b[k] for k in ['E','P','M','H','I','U','D','src']]
 additions_pt=[
 E('Madeira y Porto Santo',1425,None,U(P(-16.93,32.65),P(-16.34,33.06)),note='Poblamiento portugués desde la década de 1420; faltaban en la capa peninsular'),
 E('Azores',1439,None,U(P(-25.5,37.75),P(-27.2,38.7),P(-31.13,39.46)),note='Autorización de poblamiento de 1439; puntos de los grupos oriental, central y occidental'),
 E('Arguín',1448,1633,P(-16.46,20.6),'influence','Factoría y fortaleza insular portuguesa frente a Mauritania; no dominio del interior'),
 E('Kilwa · Quíloa',1505,1512,P(39.52,-8.96),'influence','Fortaleza portuguesa; no soberanía sobre toda la actual Tanzania'),
 E('Isla de Mozambique',1507,1975,P(40.73,-15.03),'influence','Capital y factoría insular; se conserva como punto aunque figure el contorno continental acumulado'),
 E('Sofala',1505,1898,P(34.73,-20.17),'influence','Fortaleza y factoría del litoral mozambiqueño'),
 E('Zanzíbar portugués',1503,1698,P(39.19,-6.16),'dependent','Dependencia y presencia costera de intensidad variable; expulsión por Omán'),
 E('Cananor · Kannur',1505,1663,P(75.37,11.87),'influence','Fuerte de Santo António; transferido a los neerlandeses'),
 E('Chaul',1521,1740,P(72.92,18.55),'influence','Fortaleza costera portuguesa, no toda la región del Decán'),
 E('Baçaim · Vasai',1534,1739,P(72.81,19.33),'influence','Plaza del Estado de la India; caída ante los marathas'),
 E('Dadra y Nagar Haveli',1783,1954,U(P(72.97,20.32),P(73.01,20.19)),note='Adquisiciones entre 1783 y 1785; fin del control portugués en 1954'),
 E('Solor',1566,1646,P(123.06,-8.43),'influence','Fortaleza portuguesa con interrupciones y disputa neerlandesa; no dominio continuo del archipiélago'),
 E('Flores · Larantuka',1561,1859,P(122.98,-8.34),'influence','Red luso-católica de asentamientos; derechos portugueses cedidos en el tratado de 1859, sin control uniforme de Flores'),
 ]
 b['PORT'].extend(additions_pt)
 # La capa de 1994 omite islas occidentales y anticipaba la conquista final de Canarias.
 b['SPAIN'][0]['spec']=M('Spain',clip=(-10,35,5,44))
 b['SPAIN'].extend([
 E('Canarias · islas incorporadas antes de 1479',1479,None,U(P(-13.55,28.96),P(-14.0,28.4),P(-17.13,28.1),P(-17.98,27.73)),note='Lanzarote, Fuerteventura, La Gomera y El Hierro; el mapa de la monarquía comienza en 1479, no en su primera conquista'),
 E('Gran Canaria',1483,None,P(-15.6,27.96),note='Fin de la conquista castellana en 1483'),
 E('La Palma',1493,None,P(-17.86,28.67),note='Fin de la conquista castellana en 1493; omitida en la base simplificada'),
 E('Tenerife',1496,None,P(-16.55,28.3),note='Fin de la conquista en 1496; no se anticipa a 1479'),
 E('Islas Alhucemas',1673,None,P(-3.89,35.21),note='Peñón e islotes ocupados desde agosto de 1673'),
 E('Madeira · unión dinástica',1580,1640,U(P(-16.93,32.65),P(-16.34,33.06)),'dependent','Archipiélago portugués bajo la corona compartida; mantiene su administración'),
 E('Azores · unión dinástica',1583,1640,U(P(-25.5,37.75),P(-27.2,38.7),P(-31.13,39.46)),'dependent','La resistencia de Terceira termina en 1583; no se confunde unión de coronas con anexión castellana'),
 E('Cabo Verde · unión dinástica',1580,1640,P(-23.5,15.1),'dependent','Territorio portugués durante la unión de coronas'),
 E('Santo Tomé y Príncipe · unión dinástica',1580,1640,U(P(6.73,.33),P(7.41,1.61)),'dependent','Islas portuguesas durante la unión de coronas'),
 E('Guinea portuguesa · Cacheu',1588,1640,P(-16.16,12.27),'dependent','Factoría portuguesa durante la unión; no se traslada al siglo XVI todo el país moderno'),
 E('Mozambique · unión dinástica',1580,1640,U(P(40.73,-15.03),P(34.73,-20.17)),'dependent','Factorías del Estado de la India durante la unión, sin rellenar el interior moderno'),
 E('Mombasa · unión dinástica',1593,1640,P(39.68,-4.06),'dependent','Fuerte Jesús portugués bajo los reyes de ambas coronas'),
 E('Ceilán portugués · unión dinástica',1580,1640,U(P(79.85,6.93),P(80.22,6.03)),'dependent','Enclaves y litoral portugués; Kandy permanecía independiente'),
 ])
 b['BRIT'].extend([
 E('África del Sudoeste · mandato sudafricano',1920,1966,M('Namibia'),'dependent','Mandato ejercido por la Unión Sudafricana, entonces dominio; revocado por la ONU en 1966. La ocupación sudafricana posterior no fue administración británica'),
 E('Walvis Bay',1878,1994,P(14.51,-22.96),note='Anexión británica y administración por el Cabo; Sudáfrica la transfiere a Namibia en 1994'),
 E('Togoland británico',1916,1956,I(M('Ghana'),H(1914,'Togoland')),'dependent','Parte occidental del antiguo Togoland; mandato desde 1922 y unión con la Costa de Oro tras el plebiscito de 1956. Contorno generalizado'),
 E('Zanzíbar británico',1890,1963,U(P(39.19,-6.16),P(39.77,-5.2)),'dependent','Protectorado sobre Zanzíbar y Pemba, distinto de Tanganica'),
 E('Tristán de Acuña',1816,None,P(-12.28,-37.11)),
 E('Ascensión',1815,None,P(-14.36,-7.95)),
 E('Chagos · administración británica',1814,None,P(72.41,-7.31),note='Dependencia de Mauricio y, desde 1965, BIOT. La fecha final no se da por consumada mientras la transferencia siga pendiente'),
 E('Tánger inglés',1661,1684,P(-5.81,35.78),note='Dote de Catalina de Braganza; evacuado en 1684'),
 E('Camerún septentrional británico',1916,1961,P(13.4,10.5),'dependent','Zona del mandato incorporada a Nigeria en 1961; el punto evita atribuirle un rectángulo inventado'),
 E('Nueva Guinea · ocupación y mandato australianos',1914,1975,M('Papua New Guinea'),'dependent','Acumulado del norte exalemán, Bismarck y Papúa; ocupación australiana desde 1914, mandato desde 1921. No era administración directa de Londres; interrupción japonesa en parte del territorio'),
 E('Nuevas Hébridas · Vanuatu',1906,1980,P(168.32,-17.74),'dependent','Condominio franco-británico, no colonia exclusivamente británica'),
 E('Islas Ellice · Tuvalu',1892,1978,P(179.19,-8.52),'dependent','Protectorado, luego colonia de Gilbert y Ellice; separación en 1975'),
 E('Nauru',1914,1968,P(166.93,-.53),'dependent','Ocupación australiana de 1914; mandato conjunto británico, australiano y neozelandés desde 1920, administrado por Australia; interrupción japonesa 1942–1945'),
 E('Samoa Occidental',1914,1962,P(-171.76,-13.83),'dependent','Ocupación y posterior mandato de Nueva Zelanda; no incluye Samoa Americana'),
 E('Islas Cook',1888,1965,P(-159.78,-21.23),'dependent','Protectorado británico; anexionadas a Nueva Zelanda en 1901; autogobierno en libre asociación desde 1965'),
 E('Niue',1900,1974,P(-169.92,-19.05),'dependent','Protectorado británico y administración neozelandesa desde 1901; libre asociación desde 1974'),
 E('Tokelau',1889,None,P(-171.85,-9.2),'dependent','Protectorado británico, después administración neozelandesa desde 1926; no soberanía directa británica actual'),
 E('Pitcairn',1838,None,P(-130.1,-25.07),note='Territorio británico del Pacífico; constitución de 1838'),
 E('Islas Fénix',1889,1979,P(-171.72,-2.82),note='Incorporación británica gradual desde 1889; integradas en Gilbert y Ellice en 1937'),
 E('Isla de Navidad · Kiritimati',1888,1979,P(-157.4,1.87),note='Isla de las Espóradas ecuatoriales; distinta de Christmas Island en el Índico'),
 E('Christmas Island · Índico',1888,1958,P(105.63,-10.49),note='Anexión británica; transferida a Australia en 1958'),
 E('Cocos · Keeling',1857,1955,P(96.85,-12.16),note='Anexión británica; administración transferida a Australia en 1955'),
 E('Islas Caimán',1670,None,P(-81.25,19.31)),
 E('Islas Vírgenes Británicas',1672,None,P(-64.62,18.43)),
 E('Georgia del Sur',1775,None,P(-36.75,-54.3),note='Reclamación y administración británicas, disputadas por Argentina; no implica reconocimiento de soberanía'),
 ])
 # Propagar también las correcciones a la vista conjunta: sus listas se copiaron antes.
 b['iberia']['entries']=b['regroup'](b['SPAIN'],'es')+b['regroup'](b['PORT'],'pt')
 british_sources=[src('Archivo Nacional británico: países, colonias y mandatos','https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/other-countries/'),src('ONU: mandato sobre África del Sudoeste y su revocación','https://peacekeeping.un.org/sites/default/files/past/untagFT.htm'),src('Archivos Nacionales de Australia: Papúa y Nueva Guinea','https://www.naa.gov.au/help-your-research/fact-sheets/records-papua-new-guinea-1883-1942'),src('Gobierno de Nueva Zelanda: islas del Pacífico y administración','https://teara.govt.nz/en/pacific-islands-and-new-zealand'),src('DFAT: mandato y administración conjunta de Nauru','https://www.dfat.gov.au/about-us/publications/historical-documents/Pages/volume-12/35-cabinet-submission-by-chifley-and-chambers')]
 pt_sources=[src('Madeira: historia y poblamiento','https://www.visitmadeira.com/en/what-to-do/culture-passionates/history/'),src('Gobierno de Azores: autorización de poblamiento de 1439','https://turismo.azores.gov.pt/sao-miguel/'),src('UNESCO: isla de Mozambique','https://whc.unesco.org/en/list/599'),src('UNESCO: fortaleza portuguesa de Kilwa','https://whc.unesco.org/en/list/144/'),src('Fundación Calouste Gulbenkian: Arguín','https://hpip.org/en/Contents/Place/221'),src('Censo de la India: Dadra y Nagar Haveli','https://censusindia.gov.in/nada/index.php/catalog/363/download/1100/DH_2011_2601_PART_B_DCHB_DADRA_NAGAR_HAVELI.pdf')]
 b['britain']['sources']+=british_sources
 b['portugal']['sources']+=pt_sources
 b['spain']['sources'] += [src('Defensa: incorporación de Alhucemas en 1673','https://www.boe.es/biblioteca_juridica/abrir_pdf.php?id=PUB-DH-2026-418')]
 b['spain']['sources'] += [src('Gobierno de Canarias: historia del archipiélago','https://www.gobiernodecanarias.org/transparencia/temas/institucional-organizativa/instituciones/informacion-sobre-las-islas-canarias/prehistoria-e-historia-de-canarias/')]
 b['iberia']['sources']=b['spain']['sources']+b['portugal']['sources'][1:]
 for key in ['spain','portugal','iberia','britain']:
  b[key]['limits']+=' Revisión 06-11-2026: se restituyen archipiélagos, enclaves y mandatos omitidos. Un punto localiza el caso y no rellena el territorio interior. Las fechas de inicio de posesiones agrupadas aproximan procesos graduales; las interrupciones se explican en la ficha.'

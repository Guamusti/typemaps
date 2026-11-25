"""Prospectiva editorial a 2101. Los rangos no son probabilidades estadísticas."""
AS_OF='2026-11-06'
SOURCES={
 'boug':('PNG: debate parlamentario de Bougainville, 22-10-2026','https://www.pmnec.gov.pg/pm-marape-calls-for-historic-peaceful-and-consensual-resolution-to-bougainville-referendum-as-parliament-begins-landmark-debate/'),
 'boug-law':('Acuerdo de Paz de Bougainville','https://abg.gov.pg/peace-agreement'),
 'somali':('AP: reconocimiento israelí de Somalilandia y visita diplomática','https://apnews.com/article/2447736e7355da4ac1ed182771f2e85e'),
 'green':('Gobierno danés: autogobierno y marco constitucional','https://stm.dk/statsministeriet/rigsfaellesskabet/'),
 'faroe':('Gobierno feroés: estatuto constitucional','https://www.government.fo/en/foreign-relations/constitutional-status'),
 'eu':('Comisión Europea: informes de ampliación de 2026','https://enlargement.ec.europa.eu/enlargement-policy/strategy-and-reports_en'),
 'eu-treaty':('Unión Europea: tratados vigentes','https://european-union.europa.eu/principles-countries-history/principles-and-values/founding-agreements_en'),
 'osce':('OSCE: proceso de arreglo de Transnistria','https://moldova.osce.org/'),
 'georgia':('UE y Georgia: integridad territorial y regiones separadas','https://www.eeas.europa.eu/georgia/european-union-and-georgia_en'),
 'cyprus':('ONU: resolución 2815 (2026), marco federal chipriota','https://mandates.un.org/mandate/S/RES/2815%20%282026%29?subject=Varosha+%28Cyprus%29'),
 'bosnia':('OHR: límites constitucionales a la secesión, 14-09-2026','https://www.ohr.int/ustavni-poredak-bosne-i-hercegovine-ne-moze-biti-predmet-jednostrane-revizije/'),
 'gagauz':('Comisión de Venecia: autonomía gagauza y autodeterminación condicionada','https://www.venice.coe.int/webforms/documents/default.aspx?pdffile=CDL-INF%282000%29016-e'),
 'ireland':('Acuerdo de Belfast: principio de consentimiento','https://www.gov.uk/government/publications/the-belfast-agreement'),
 'scotland':('Tribunal Supremo británico: referéndum escocés','https://www.supremecourt.uk/cases/uksc-2022-0098'),
 'caledonia':('Asamblea Nacional: rechazo de la reforma, 02-04-2026','https://www.assemblee-nationale.fr/dyn/actualites-accueil-hub/rejet-du-projet-de-loi-constitutionnelle-relatif-a-la-nouvelle-caledonie'),
 'chagos':('AP: suspensión del acuerdo de Chagos, abril de 2026','https://apnews.com/article/c37afa22677ec8e504c5a1dab6313d1c'),
 'sahara':('ONU: resolución 2797 (2025) y negociación de estatuto','https://digitallibrary.un.org/record/4093660/files/S_RES_2797_%282025%29-EN.pdf'),
 'palestine':('ONU: dos Estados y líneas anteriores a 1967, 22-09-2026','https://www.un.org/unispal/document/sg-statement-22sep26/'),
 'ukraine':('ONU: integridad territorial de Ucrania, 01-09-2026','https://www.un.org/pga/80/2026/09/01/pga-remarks-review-on-the-occasion-of-the-international-day-against-nuclear-tests/'),
 'sudan':('ONU: unidad e integridad territorial de Sudán, 10-09-2026','https://dppa.un.org/en/press-releases/statement-of-the-quintet-visit-to-khartoum'),
 'yemen':('ONU: fragmentación y proceso político en Yemen, octubre de 2026','https://unric.org/en/yemen-general-collapse-and-resumption-of-fighting/'),
 'syria':('ONU: acuerdo de integración del noreste sirio, 30-01-2026','https://www.un.org/sg/en/content/sg/statements/2026-01-30/statement-attributable-the-spokesperson-for-the-secretary-general-syria'),
 'eac':('Comunidad de África Oriental: proyecto de federación','https://www.eac.int/political-federation'),
 'puerto':('Congreso de Estados Unidos: opciones de estatuto de Puerto Rico','https://www.congress.gov/crs_external_products/R/PDF/R44721/R44721.8.pdf'),
 'quebec':('Tribunal Supremo de Canadá: negociación de una secesión','https://scc-csc.lexum.com/scc-csc/bulletins/en/153/1/document.do'),
 'belgium':('Bélgica: comunidades, regiones y Estado federal','https://www.belgium.be/en/about_belgium/government/federale_staat'),
 'jamaica':('Gobierno jamaicano: proyecto de reforma republicana','https://roadtorepublic.mlca.gov.jm/republic-bill-publications/'),
 'chat':('Conversación de origen: Probable Border Changes','https://chatgpt.com/c/6aed2981-fd64-83eb-9821-09250f440dca'),
 'ne':('Natural Earth: datos y convenciones cartográficas','https://www.naturalearthdata.com/about/disputed-boundaries-policy/'),
}
LEVELS={
 'process':dict(label='Proceso formal encaminado',color='#398d7c',order=0),
 'plausible':dict(label='Cambio plausible, condicionado',color='#638ab6',order=1),
 'uncertain':dict(label='Desenlace muy incierto',color='#c7944e',order=2),
 'context':dict(label='Continuidad / contexto',color='#8f9799',order=3),
}
CASES=[]
def add(key,name,area,coords,level,kind,current,outlook,gate,refs,geo,central=False):
 CASES.append(dict(id=key,name=name,region=area,lon=coords[0],lat=coords[1],level=level,kind=kind,current=current,outlook=outlook,conditions=gate,sourceKeys=refs,geo=geo,central=central))

add('bougainville','Bougainville','Pacífico',(155.3,-6.2),'process','Independencia',
 'Región autónoma de Papúa Nueva Guinea. El referéndum de 2019 favoreció la independencia; el Parlamento nacional conserva la decisión final.',
 'Independencia negociada: uno de los candidatos más sólidos a nuevo Estado. El horizonte no fija una fecha de consumación.',
 'Ratificación parlamentaria, transición y acuerdo sobre financiación y competencias. Los objetivos de 2027/2030 no son fechas garantizadas.',
 ['boug','boug-law'],dict(admin1Code='PG-NSB'),True)
add('somaliland','Somalilandia','África',(46,9.7),'plausible','Reconocimiento',
 'Administración separada desde 1991. Israel la reconoció en diciembre de 2025; Somalia rechaza su separación. El control oriental es disputado.',
 'Ampliación del reconocimiento y posible consolidación diplomática. No se trata de crear de cero una entidad ni de garantizar su entrada en la ONU.',
 'Reconocimientos adicionales, acuerdo regional y solución de disputas locales. Su contorno de referencia no representa control efectivo uniforme.',
 ['somali'],dict(country='Somaliland'),True)
add('kosovo','Kosovo','Europa',(20.9,42.6),'plausible','Reconocimiento',
 'Estado de reconocimiento parcial desde 2008; Serbia no reconoce su independencia.',
 'Normalización y mayor reconocimiento son más defendibles como hipótesis que una nueva partición territorial automática.',
 'Negociación con Serbia, derechos de comunidades y decisiones de los Estados que todavía no lo reconocen.',
 ['eu','chat'],dict(country='Kosovo'),True)
add('greenland','Groenlandia','Atlántico / Ártico',(-42,71),'plausible','Independencia',
 'Territorio autónomo del Reino de Dinamarca, con marco de autogobierno y posibilidad de decidir su futuro.',
 'La independencia negociada es una posibilidad relevante a largo plazo; no se considera consumada en el mapa central.',
 'Voluntad ciudadana, acuerdo con Dinamarca, sostenibilidad fiscal y arreglos de seguridad. No se presupone anexión por otro país.',
 ['green'],dict(country='Greenland'))
add('faroe','Islas Feroe','Atlántico',(-6.9,62),'plausible','Independencia',
 'Autogobierno dentro del Reino de Dinamarca, con amplias competencias propias.',
 'Más competencias o independencia negociada son opciones de largo plazo; continuidad autonómica sigue siendo viable.',
 'Mandato político sostenido, negociación constitucional y solución fiscal y monetaria.',
 ['faroe'],dict(country='Faroe Islands'))
add('caledonia','Nueva Caledonia','Pacífico',(165.5,-21.3),'plausible','Estatuto constitucional',
 'Territorio francés con proceso de descolonización y conflicto de estatuto. La reforma constitucional fue rechazada en primera lectura en abril de 2026.',
 'Un nuevo acuerdo institucional es plausible; mayor autonomía no equivale por sí sola a independencia.',
 'Acuerdo local inclusivo, reforma constitucional y procedimientos de aprobación. No dar por implantado el acuerdo de Bougival.',
 ['caledonia'],dict(country='New Caledonia'))
add('chagos','Archipiélago de Chagos','Índico',(72,-6),'uncertain','Transferencia de soberanía',
 'El tratado de transferencia a Mauricio firmado en 2025 quedó en suspenso en 2026; persisten cuestiones sobre la base y la población chagosiana.',
 'Transferencia pactada de soberanía es una posibilidad concreta, pero no se trata como un hecho ya ratificado.',
 'Reactivación y ratificación del acuerdo, arreglos de defensa y atención a los derechos de los chagosianos.',
 ['chagos'],dict(country='British Indian Ocean Territory'))
add('scotland','Escocia','Europa',(-4,57),'plausible','Independencia',
 'Nación constitutiva del Reino Unido, con gobierno y Parlamento propios.',
 'Independencia negociada es plausible en un horizonte largo, sin asumir mayoría estable ni fecha para otro referéndum.',
 'Mandato democrático y vía constitucional acordada; el referéndum unilateral no fue avalado por el Tribunal Supremo.',
 ['scotland'],dict(geonunit='Scotland'))
add('ireland','Irlanda del Norte','Europa',(-6.7,54.7),'plausible','Reunificación',
 'Parte del Reino Unido, sujeta al principio de consentimiento del Acuerdo de Belfast.',
 'Una Irlanda unificada es una alternativa de largo plazo; la frontera solo cambia si se cumplen los procedimientos democráticos.',
 'Mayorías y procesos de aprobación correspondientes en la isla. No inferir el resultado solo a partir de la demografía.',
 ['ireland'],dict(geonunit='Northern Ireland'))
add('eu-enlargement','Ampliación de la Unión Europea','Europa',(20.5,47.5),'process','Integración supranacional',
 'Montenegro, Albania, Moldavia y Ucrania cuentan con procesos de adhesión e informes de progreso en 2026.',
 'Una UE más amplia es un cambio de integración relativamente encaminado. Las fronteras nacionales no desaparecen por adherirse.',
 'Reformas, negociación de capítulos y ratificaciones. No se fija un año de ingreso ni se asegura que los cuatro entren a la vez.',
 ['eu'],dict(countries=['Montenegro','Albania','Moldova','Ukraine']),True)
add('eu-federal','Núcleo federal europeo','Europa',(7,50),'uncertain','Federación',
 'La UE reúne soberanías y ejerce competencias comunes; no es un único Estado federal.',
 'Mayor integración o un núcleo federal son escenarios posibles. La creación de un solo país europeo no es el desenlace central.',
 'Cambios de tratados, ratificaciones y definición de participantes. El área dibujada solo localiza la UE actual, no una membresía federal predicha.',
 ['eu-treaty'],dict(eu=True))
add('moldova-romania','Moldavia y Rumanía','Europa',(27.8,46.8),'uncertain','Unificación',
 'Dos Estados soberanos; Moldavia mantiene además el problema de Transnistria y la autonomía gagauza.',
 'La integración europea sin unificación estatal es la trayectoria central; una unión política exige cambios adicionales.',
 'Consentimiento ciudadano y constitucional y acuerdos sobre autonomías, ciudadanía y territorios no controlados.',
 ['osce','eu'],dict(countries=['Moldova','Romania']))
add('transnistria','Transnistria','Europa',(29.2,47.2),'uncertain','Reintegración / estatuto',
 'Región separada de facto de Moldavia. El marco de la OSCE respalda un estatuto especial dentro de Moldavia.',
 'Reintegración negociada o continuidad de facto son alternativas más sólidas para el mapa central que una independencia internacional asegurada.',
 'Seguridad regional, presencia rusa, acuerdo Chisináu–Tiráspol y garantías. No comparte frontera terrestre con Rusia.',
 ['osce'],dict(disputed='Transnistria'))
add('gagauzia','Gagauzia','Europa',(28.65,46.3),'context','Autonomía condicionada',
 'Autonomía de Moldavia. Su marco legal contiene una cláusula condicionada al cambio del estatuto independiente de Moldavia.',
 'Continuidad autonómica es la referencia; una hipotética unión moldavo-rumana abriría una controversia específica.',
 'No existe independencia automática. Habría que resolver interpretación, procedimiento y reconocimiento.',
 ['gagauz'],dict(admin1Code='MD-GA'))
add('abkhazia','Abjasia','Cáucaso',(40.8,43.1),'uncertain','Estatuto de facto',
 'Separada del control georgiano, con reconocimiento limitado y fuerte dependencia rusa; el marco internacional mantiene su pertenencia a Georgia.',
 'Continuidad de facto es la hipótesis prudente. Reintegración, mayor reconocimiento o mayor integración rusa son desenlaces alternativos.',
 'Seguridad, política rusa, acuerdo con Georgia y derechos de población desplazada. No se da por hecha una anexión a Rusia.',
 ['georgia'],dict(disputed='Abkhazia'))
add('south-ossetia','Osetia del Sur','Cáucaso',(44.05,42.35),'uncertain','Estatuto de facto',
 'Fuera del control georgiano, reconocida por Rusia y pocos Estados; internacionalmente tratada mayoritariamente como parte de Georgia.',
 'La continuidad de facto se mantiene como referencia. Una incorporación a Rusia es una opción política, no una consecuencia inevitable.',
 'Decisiones rusas, arreglo regional y oposición georgiana. Osetia del Norte ya pertenece a Rusia; no se inventa una nueva frontera entre ambas.',
 ['georgia'],dict(disputed='South Ossetia'))
add('adjara','Adjaria','Cáucaso',(41.9,41.7),'context','Autonomía interna',
 'República autónoma bajo control de Georgia, diferenciada de Abjasia y Osetia del Sur.',
 'Continuidad autonómica dentro de Georgia. No hay base para clasificarla como uno de los próximos Estados más probables.',
 'Una transformación del autogobierno no implicaría por sí misma nuevas fronteras internacionales.',
 ['georgia','chat'],dict(admin1Code='GE-AJ'))
add('karabakh','Nagorno-Karabaj','Cáucaso',(46.6,39.8),'context','Cambio ya ocurrido',
 'Bajo control de Azerbaiyán desde 2023; la administración separatista dejó de ejercer el poder sobre el territorio.',
 'Acuerdo de paz, derechos y retorno son asuntos abiertos. No se dibuja Artsaj como nuevo Estado probable.',
 'La capa conserva el contorno histórico para localizar el caso; su antigua etiqueta de entidad separatista no describe la situación actual.',
 ['chat','ne'],dict(disputed='Artsakh'))
add('srpska','Republika Srpska','Europa',(18,44.5),'uncertain','Reforma federal / secesión',
 'Entidad constitutiva de Bosnia y Herzegovina; no es un Estado independiente de facto equivalente a Transnistria.',
 'Reorganización institucional o continuidad federal son la referencia; una secesión o unión con Serbia es un escenario conflictivo e incierto.',
 'Acuerdo constitucional y garantías. Dayton no otorga un derecho de secesión unilateral; Brčko tiene estatuto propio.',
 ['bosnia'],dict(srpska=True))
add('vojvodina','Voivodina','Europa',(19.7,45.4),'context','Autonomía interna',
 'Provincia autónoma de Serbia; su autonomía no equivale a soberanía internacional.',
 'Evolución de competencias o de organización interna; independencia no se coloca entre los desenlaces centrales.',
 'Reformas políticas y constitucionales serbias. No se confunde autonomía regional con secesión.',
 ['chat','ne'],dict(vojvodina=True))
add('sandzak','Sandžak','Europa',(20.5,43.1),'context','Cooperación / autonomía',
 'Región histórica entre Serbia y Montenegro, sin una unidad administrativa transfronteriza única.',
 'Cooperación municipal y protección cultural son más defendibles que una nueva frontera internacional predicha.',
 'Se usa un marcador de localización en Novi Pazar; no se inventa un contorno administrativo unificado.',
 ['chat'],dict(point=True))
add('north-cyprus','Norte de Chipre','Mediterráneo',(33.5,35.3),'uncertain','Reunificación / partición',
 'Administración turcochipriota reconocida como Estado solo por Turquía; la isla sigue dividida de facto.',
 'Continuidad de la división o arreglo federal son alternativas. La ONU mantiene un marco bicomunal y bizonal, no dos Estados ya acordados.',
 'Acuerdo entre comunidades y garantes. Las bases soberanas británicas no desaparecen automáticamente.',
 ['cyprus'],dict(country='Northern Cyprus'))
add('western-sahara','Sáhara Occidental','África',(-12.3,24.8),'uncertain','Arreglo de soberanía',
 'Territorio en disputa, con control dividido y proceso político de la ONU.',
 'Un acuerdo de estatuto es plausible; la autonomía bajo soberanía marroquí tiene impulso diplomático, sin equivaler a un arreglo final ya aceptado.',
 'Negociación y autodeterminación en el marco de la ONU. No se da por consumada una anexión ni una independencia.',
 ['sahara'],dict(country='Western Sahara'))
add('palestine','Palestina','Mediterráneo',(35.2,31.8),'uncertain','Reconocimiento / soberanía efectiva',
 'Reconocimiento internacional amplio pero soberanía efectiva, seguridad y límites sin resolver.',
 'Mayor consolidación diplomática y una solución de dos Estados son horizontes políticos, no una frontera final predecible.',
 'Acuerdos sobre territorio, Jerusalén, seguridad y derechos. El contorno de referencia no es una propuesta de reparto de Gaza o Cisjordania.',
 ['palestine'],dict(country='Palestine'))
add('ukraine','Ucrania','Europa',(34,49),'uncertain','Arreglo territorial / control',
 'La soberanía internacionalmente reconocida y el control militar no coinciden en parte del territorio.',
 'No hay base sólida para dibujar una frontera definitiva de paz a 2101. Se mantiene la distinción entre soberanía y control.',
 'Resultado de la guerra, acuerdos y reconocimiento. No se extrapola una línea de frente actual como frontera permanente.',
 ['ukraine'],dict(country='Ukraine'))
add('yemen','Yemen','Asia',(47,15.5),'uncertain','Descentralización / partición',
 'Estado fragmentado por la guerra; el principal movimiento separatista sureño sufrió un retroceso en 2026.',
 'Un arreglo descentralizado compite con una partición negociada. No se restauran automáticamente los dos Estados anteriores a 1990.',
 'Acuerdo inclusivo y situación de las autoridades locales. Las antiguas fronteras no se presentan como la futura línea acordada.',
 ['yemen'],dict(country='Yemen'))
add('sudan','Sudán','África',(30,15),'uncertain','Fragmentación / descentralización',
 'La guerra ha producido autoridades territoriales rivales, sin convertir sus zonas de control en Estados reconocidos.',
 'La fragmentación duradera es un riesgo; un arreglo interno sigue siendo una alternativa. No se predice una nueva frontera de Darfur.',
 'Cese de la guerra y proceso político. La ONU defiende la unidad e integridad territorial; el fondo no muestra frentes actuales.',
 ['sudan'],dict(country='Sudan'))
add('syria-kurds','Noreste de Siria','Asia',(41.1,36.6),'plausible','Integración / autonomía',
 'Los acuerdos de enero de 2026 apuntan a integrar estructuras kurdas y del noreste en el Estado sirio.',
 'Integración pactada con garantías y derechos culturales es la trayectoria de referencia, antes que un Estado kurdo independiente.',
 'Aplicación real de los acuerdos y garantías locales. El marcador no dibuja zonas militares actuales.',
 ['syria'],dict(point=True),True)
add('korea','Península coreana','Asia',(127.5,38),'uncertain','Reunificación',
 'Dos Estados separados con sistemas e intereses de seguridad muy distintos.',
 'Reunificación posible en un horizonte muy largo, pero no suficientemente encaminada para convertirla en el mapa central.',
 'Acuerdo político, seguridad nuclear e implicación de las potencias vecinas. No se fija el régimen de una Corea unida.',
 ['chat'],dict(countries=['North Korea','South Korea']))
add('taiwan','Taiwán','Asia',(121,23.7),'uncertain','Estatuto / integración',
 'Autogobierno efectivo y un estatuto internacional disputado en el marco de la relación con la República Popular China.',
 'Continuidad de facto, acuerdo o conflicto son alternativas de gran incertidumbre; no se afirma una incorporación inevitable a la RPC.',
 'Decisiones locales, políticas de Pekín y entorno de seguridad. Una reclamación territorial no equivale a control efectivo.',
 ['chat','ne'],dict(country='Taiwan'))
add('catalonia','Cataluña','Europa',(1.7,41.7),'context','Autonomía / independencia',
 'Comunidad autónoma española con movimiento independentista y debate sobre su encaje territorial.',
 'Reforma de competencias o acuerdos políticos son más prudentes como referencia que independencia asegurada.',
 'Mandato político y procedimiento constitucional. No se representa toda región con identidad propia como un futuro país.',
 ['chat'],dict(admin1Code='ES-CT'))
add('quebec','Quebec','América',(-71.5,50),'context','Independencia negociada',
 'Provincia canadiense con antecedentes de referéndums soberanistas.',
 'La continuidad provincial es la referencia; una nueva secesión negociada requeriría un cambio político sostenido.',
 'Pregunta clara, mayoría clara y negociación constitucional; ninguna independencia automática por una consulta aislada.',
 ['quebec'],dict(admin1Code='CA-QC'))
add('belgium','Bélgica','Europa',(4.6,50.7),'context','Reforma federal',
 'Estado federal organizado en comunidades y regiones.',
 'Más redistribución interna de competencias es una posibilidad; una partición en países distintos no es el escenario central.',
 'Acuerdos entre comunidades y resolución de cuestiones como Bruselas. El federalismo existente no demuestra una ruptura futura.',
 ['belgium'],dict(country='Belgium'))
add('puerto-rico','Puerto Rico','Caribe',(-66.4,18.2),'plausible','Cambio de estatuto',
 'Territorio de Estados Unidos con alternativas de estadidad, independencia o libre asociación.',
 'Una solución de estatuto es plausible; no se da por aprobada la admisión como estado ni se equipara esta a independencia.',
 'Mandato local y actuación del Congreso estadounidense. Los proyectos legislativos no constituyen una ley aprobada.',
 ['puerto'],dict(country='Puerto Rico'))
add('west-papua','Papúa occidental','Pacífico',(135,-4),'context','Autonomía / secesión',
 'Parte de Indonesia, con conflictos y movimientos independentistas.',
 'No hay un proceso de independencia comparable al de Bougainville; no se asigna una separación al mapa central.',
 'Serían necesarios cambios políticos y acuerdos sustanciales. El área dibujada es regional, no un Estado futuro delimitado.',
 ['chat'],dict(westPapua=True))
add('tibet','Tíbet','Asia',(88,32),'context','Autonomía / secesión',
 'Territorio bajo soberanía y administración chinas; autonomía y reivindicaciones políticas no equivalen a independencia efectiva.',
 'No se incorpora una independencia al mapa central. Cambios de derechos o autogobierno no crearían necesariamente una frontera internacional.',
 'La geometría localiza la región administrativa; no pretende representar toda definición cultural o histórica del Tíbet.',
 ['chat'],dict(admin1Code='CN-XZ'))
add('eac','África Oriental · integración','África',(32,-3),'plausible','Confederación / federación',
 'La Comunidad de África Oriental contempla una confederación como transición hacia un proyecto federal.',
 'Más integración es plausible; un único Estado federal con todos los miembros y una fecha concreta no está garantizado.',
 'Constitución pactada, consultas, ratificaciones y definición de participantes. Se localiza el espacio regional, no un país ya creado.',
 ['eac'],dict(countries=['Kenya','Uganda','United Republic of Tanzania','Rwanda','Burundi','South Sudan','Democratic Republic of the Congo','Somalia']))
add('jamaica','Jamaica y reformas republicanas','Caribe',(-77.3,18.1),'plausible','Reforma constitucional',
 'Jamaica es un Estado soberano; el debate republicano afecta a su jefatura del Estado.',
 'Una república puede sustituir a la monarquía compartida sin cambiar las fronteras ni crear un nuevo país.',
 'Reforma y aprobación interna. No se colorea como independencia de un territorio que ya es soberano.',
 ['jamaica'],dict(country='Jamaica'),True)

concavity:

- pocket
- void
- channel
- mouth
- groove
- depression
- cleft
- bottleneck

convexity:

- protrusion
- knob
- bulge
- spike
- ridge
- convexpatch

mix:

- interface
- surfacepatch
- interfacepatch

Concavity	Pocket, Channel, Cavity, Mouth, Groove, Depression, Cleft	Sitios de unión, túneles, interfaces receptoras
Convexity	Protrusion, Knob, Bulge, SurfaceSpike, InterfacePatch	Interacciones PPI, epítopos, hotspots de reconocimiento


Pocket, Cavity, Channel, Mouth,
Interface, Groove, Depression,
Cleft, SurfacePatch,
Bottleneck, Void

TopographicCluster, CavityGraph


Cavity puede ser la clase general y pocket, channel y void sus subtipos (cavity_type).
Mouth debe mantenerse como entidad independiente, ya que se asocia a varios tipos de features.
Interface y Groove te dan espacio para crecer hacia interacciones complejas (PPI, membranas, ácidos nucleicos).
La taxonomía es compatible con herramientas de alpha-shapes y con outputs de CASTp/fpocket/MOLE.

🧪 3. Clasificación funcional (opcional)
Estas etiquetas no son clases en sí mismas, pero pueden ser atributos (feature_type o functional_role) para enriquecer los objetos:

binding_site
active_site
allosteric_site
transmembrane_channel
protein_protein_interface
protein_ligand_interface
cryptic_site (detectado dinámicamente)
transient_pocket


 Entidades principales
Pocket	Depresiones accesibles desde el exterior pero con forma “de bolsa” (abiertas por una boca)	sitios de unión de ligandos
Cavity	Volúmenes cerrados en el interior de la proteína, sin acceso al solvente	voids internos
Channel	Conductos o túneles que conectan dos o más bocas externas	túneles de proteínas enzimáticas
Mouth	Abertura de acceso a un feature topográfico (pocket, cavity o channel)	entrada a un túnel
Interface	Superficie de contacto entre dos biomoléculas (o dominios)	interfaces proteína-proteína
Groove	Surcos superficiales alargados y abiertos	surcos de unión de DNA
Depression	Concavidades abiertas y poco profundas que no califican como pocket	hendiduras de superficie
SurfacePatch	Región arbitraria de superficie (útil para mapear propiedades locales)	parches hidrofóbicos
Cleft	Depresiones amplias, intermedias entre surcos y pockets	zonas de unión grandes o alargadas

🧱 2. Entidades complementarias / auxiliares
Nombre	Descripción
InterfaceMouth	Boca localizada en la frontera entre dos cadenas o complejos
Bottleneck	Estrechamiento máximo de un canal o túnel
CavityGraph	Representación de conectividad entre pockets, canales y bocas
TopographicCluster	Grupo de features espacialmente relacionados
SurfaceNode	Nodo de la malla de superficie o alpha-shape asociado a un feature
SurfaceEdge / SurfaceFace	Elementos geométricos de triangulación
Void (alias interno)	sinónimo de cavity cerrada sin bocas — útil para compatibilidad con CASTp


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

----------------

1) Tipado y contratos

Enums o StrEnum (3.11) para shape_type y quizá feature_type en el runtime,
manteniendo Literal[...] para los type-checkers. Esto te da validación en
tiempo de ejecución sin perder precisión estática.

Final para constantes (claves de diccionario como "concavity_types"), evitando reasignaciones accidentales.

TypedDict (o Protocol adicional) si data u otros blobs de metadatos tienen estructura conocida.

Mypy/pyright “strict-ish”: activa flags como warn-unused-ignores,
no_implicit_optional, disallow-any-generics, etc. (mejora la robustez con coste
bajo).

2) Modelo de datos y mutabilidad

@dataclass(slots=True) en Topography para reducir huella de memoria y acelerar
attribute access (útil con muchos features).

Inmutabilidad selectiva: considera congelar (frozen=True) algunos campos de
features (al menos feature_id, feature_type, shape_type, dimensionality,
type_index) y dejar mutables solo los contenedores (boundary_ids, point_ids).
Esto mantiene integridad sin sacrificar ergonomía.

Read-only views extra: además de tuple, si expones mapas (p.ej. una vista
pública de by_type_index), usa types.MappingProxyType para asegurar
inmutabilidad externa.

3) Errores y validación

Excepciones específicas: define una jerarquía (TopoMTError, DuplicateIDError,
TypeIndexConflict, ShapeCompatibilityError, …). Mejora el manejo aguas arriba y
los mensajes.

Chequeos de invariantes (método validate() en Topography):

Unicidad de feature_id.

Unicidad de (feature_type, type_index).

Coherencia de relaciones (parents_of/children_of, y que boundary_ids/point_ids existan solo en 2D).

Modo estricto opcional (flag de entorno o parámetro): en estricto, convierte
warnings en errores o ejecuta validaciones adicionales (útil en CI).

4) Rendimiento y escalabilidad

Compresión de índices: si el volumen crece, puedes mapear feature_type y
shape_type a enteros (tablas de símbolos) internamente; tu API seguiría usando
strings/Enums, pero reduces memoria y aceleras lookups.

Batch ops: añade register_many(iterable) y link_many(pairs) para minimizar overhead en cargas grandes.

Perfilado básico: un microbenchmark de register/link/of_type con 1e5 features para detectar cuellos (dict growth, GC).

5) Concurrencia y seguridad de hilo

Si prevés uso concurrente, añade un RLock interno y decóralo en
register/link/mutadores. Expón en docs que las vistas devueltas son
instantáneas (snapshot) no “live”.

6) Extensibilidad y plugins

Sistema de “entry points” (via importlib.metadata.entry_points) para registrar
tipos de features desde paquetes externos (plugins). Tu Topography podría
consumir un catalog loader y poblar catalog.

Hooks: callbacks opcionales (on_register, on_link) para auditar, loggear o construir índices secundarios.

7) Serialización y E/S

Define un formato estable: to_dict()/from_dict() para Topography y features,
más to_json() (o msgspec/orjson si te importa el rendimiento).

Versiona el esquema (campo schema_version) para migraciones futuras.

8) Logging y trazabilidad

Integra logging (ya lo trabajaste en otros proyectos): canaliza avisos de
compatibilidad, enlaces redundantes, etc., con niveles (INFO, WARNING, ERROR) y
un Logger de módulo.

9) Documentación y DX

Docstrings NumPy + ejemplos de uso (registro, link, consultas por tipo).

Sphinx: página “Architecture & Invariants”, “Extending with new feature types”, y “Performance tips”.

Type-directed docs: los TypeAlias y Protocol ya facilitan que la docs auto-generada sea clara.

10) Testing

Tests de propiedades con Hypothesis (p.ej., “si registras N features con
(type,type_index) únicos, nunca deben colisionar”; “si haces link válido,
parents_of(child) y children_of(parent) son consistentes”).

Fuzz tests de serialización/deserialización y round-trip.

CI: mypy/pyright + ruff/black/isort + pytest (coverage).

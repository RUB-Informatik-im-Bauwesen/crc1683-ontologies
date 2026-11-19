# /// script
# requires-python = ">=3.10"
# dependencies = ["ifcopenshell>=0.8.0", "rdflib>=7.0.0"]
# ///
"""
CERO <-> IFC adapter.

Converts the building elements of an IFC file to RDF using the Concrete
Element Reuse Ontology (CERO, https://w3id.org/cero) and back.

CERO v0.1 is a flat property dictionary: datatype properties on bot:Element,
no element classes and no object properties. Each IFC element therefore
becomes one bot:Element individual, typed additionally with its ifcOWL class.
Buildings and storeys are described with BOT, which CERO builds on. Geometry
is optional and stored as an OBJ mesh with FOG (https://w3id.org/fog).

Which IFC property fills which CERO property is defined in mapping tables
(CSV), not in code. mapping_ifc4.csv covers the standard buildingSMART
property and quantity sets. Further tables map project-specific property
sets, either to CERO or to properties in a namespace of your own, so that
values without a CERO counterpart survive the round trip.

Usage:
    python cero_ifc.py to-cero model.ifc -o out/
    python cero_ifc.py to-cero model.ifc --mapping my_psets.csv mapping_ifc4.csv
    python cero_ifc.py to-ifc out/model.ttl -o model_from_cero.ifc
    python cero_ifc.py roundtrip model.ifc
    python cero_ifc.py vocabulary --mapping my_psets.csv -o my_extension.ttl
"""

import argparse
import csv
import fnmatch
import math
import re
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple
from urllib.parse import quote

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.pset
import ifcopenshell.util.unit
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD


# ── Namespaces ───────────────────────────────────────────────────────────────

CERO = Namespace("https://w3id.org/cero#")
BOT = Namespace("https://w3id.org/bot#")
FOG = Namespace("https://w3id.org/fog#")
IFCOWL = Namespace("https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2_TC1/OWL#")
ISOPROPS = Namespace("https://w3id.org/isoprops#")
QUDT_UNIT = Namespace("http://qudt.org/vocab/unit/")

CERO_ONTOLOGY = URIRef("https://w3id.org/cero")
GEOMETRY = FOG["asObj_v3.0-obj"]

# Placeholder (example.org is reserved): pass a persistent base IRI before
# publishing any data.
DEFAULT_BASE_IRI = "https://example.org/cero/data/"

DEFAULT_MAPPING = Path(__file__).with_name("mapping_ifc4.csv")

# Elements converted by default: IfcBuiltElement replaces IfcBuildingElement
# from IFC4X3 on
DEFAULT_CLASSES = ("IfcBuildingElement", "IfcBuiltElement")

# Schema of the IFC files written by cero_to_ifc
OUTPUT_SCHEMA = "IFC4"


# ── Units ────────────────────────────────────────────────────────────────────

# Unit of an RDF value -> (SI value * factor = RDF value, QUDT unit)
UNITS: Dict[str, Tuple[float, str]] = {
    "m": (1.0, "M"), "cm": (1e2, "CentiM"), "mm": (1e3, "MilliM"),
    "m2": (1.0, "M2"), "cm2": (1e4, "CentiM2"), "mm2": (1e6, "MilliM2"),
    "m3": (1.0, "M3"),
    "m4": (1.0, "M4"), "cm4": (1e8, "CentiM4"), "mm4": (1e12, "MilliM4"),
    "kg": (1.0, "KiloGM"), "t": (1e-3, "TONNE"),
    "kg/m3": (1.0, "KiloGM-PER-M3"),
    "N": (1.0, "N"), "kN": (1e-3, "KiloN"), "MN": (1e-6, "MegaN"),
    "Nm": (1.0, "N-M"), "kNm": (1e-3, "KiloN-M"),
    "Pa": (1.0, "PA"), "MPa": (1e-6, "MegaPA"), "GPa": (1e-9, "GigaPA"),
    "rad": (1.0, "RAD"), "deg": (180.0 / math.pi, "DEG"),
    "s": (1.0, "SEC"),
}

_UNITLESS = {
    "IfcReal", "IfcInteger", "IfcBoolean", "IfcLogical", "IfcIdentifier", "IfcLabel",
    "IfcText", "IfcCountMeasure", "IfcNumericMeasure", "IfcRatioMeasure",
    "IfcNormalisedRatioMeasure", "IfcPositiveRatioMeasure", "IfcQuantityCount",
}
_QUANTITY_UNITS = {
    "IfcQuantityLength": "LENGTHUNIT", "IfcQuantityArea": "AREAUNIT",
    "IfcQuantityVolume": "VOLUMEUNIT", "IfcQuantityWeight": "MASSUNIT",
    "IfcQuantityTime": "TIMEUNIT",
}
_SIGNIFICANT_DIGITS = 15


def _unit_type(measure: str) -> Optional[str]:
    """IFC unit type of a value type or quantity class, None if it has no unit."""
    if measure in _UNITLESS:
        return None
    return _QUANTITY_UNITS.get(measure) or ifcopenshell.util.unit.get_measure_unit_type(measure)


def _named_unit_scale(unit: ifcopenshell.entity_instance) -> float:
    """Factor converting a value in an IfcNamedUnit to SI base units."""
    scale = 1.0
    while unit.is_a("IfcConversionBasedUnit"):
        scale *= unit.ConversionFactor.ValueComponent.wrappedValue
        unit = unit.ConversionFactor.UnitComponent
    if unit.is_a("IfcSIUnit"):
        scale *= ifcopenshell.util.unit.get_prefix_multiplier(unit.Prefix)
        if unit.Name == "GRAM":
            # IFC names the gram, the SI base unit is the kilogram
            scale *= 1e-3
    return scale


def _si_scale(ifc_file: ifcopenshell.file, measure: str) -> float:
    """
    Factor converting a stored IFC value of this type to SI base units,
    according to the unit assignment of the project. Types without a declared
    unit are taken as SI.
    """
    unit_type = _unit_type(measure)
    if unit_type is None:
        return 1.0
    projects = ifc_file.by_type("IfcProject")
    if not projects or not projects[0].UnitsInContext:
        return 1.0
    for unit in projects[0].UnitsInContext.Units:
        if getattr(unit, "UnitType", None) != unit_type:
            continue
        if unit.is_a("IfcDerivedUnit"):
            return math.prod(_named_unit_scale(e.Unit) ** e.Exponent for e in unit.Elements)
        return _named_unit_scale(unit)
    return 1.0


def _round(value: float) -> float:
    return float(f"{value:.{_SIGNIFICANT_DIGITS}g}")


def _literal(value) -> Literal:
    if isinstance(value, (bool, int, str)):
        return Literal(value)
    # CERO ranges are xsd:decimal, which has no exponent notation
    text = format(Decimal(repr(float(value))), "f")
    return Literal(text, datatype=XSD.decimal)


# ── Mapping tables ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PropertyMapping:
    """Maps one IFC property or quantity to one RDF datatype property."""
    ifc_class: str       # IFC class including its subclasses, or * for any element
    pset: str            # property or quantity set, may contain * (Pset_*Common)
    ifc_name: str        # name of the property or quantity
    measure: str         # IFC value type or quantity class used when writing IFC
    term: URIRef         # CERO property, or a property of another namespace
    unit: str = ""       # unit of the RDF value, a key of UNITS
    fit: str = "exact"   # exact | close | extension
    note: str = ""

    def applies_to(self, element: ifcopenshell.entity_instance) -> bool:
        return self.ifc_class == "*" or element.is_a(self.ifc_class)

    @property
    def is_quantity(self) -> bool:
        return self.measure.startswith("IfcQuantity")

    @property
    def si_to_rdf(self) -> float:
        return UNITS[self.unit][0] if _unit_type(self.measure) else 1.0


def load_mapping(paths: Sequence[Path] = (DEFAULT_MAPPING,)) -> List[PropertyMapping]:
    """
    Read mapping tables. Columns: ifc_class, pset, property, measure, term,
    unit, fit, note. A term is either cero:<name> or a full IRI.

    Rows of earlier files take precedence over rows of later files.

    Raises:
        ValueError: if a row with a dimensional value type has no known unit
    """
    mapping: List[PropertyMapping] = []
    for path in paths:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            for line, row in enumerate(csv.DictReader(handle), start=2):
                row = {key: (value or "").strip() for key, value in row.items() if key}
                term = row["term"]
                is_cero = term.startswith("cero:")
                entry = PropertyMapping(
                    ifc_class=row["ifc_class"] or "*",
                    pset=row["pset"],
                    ifc_name=row["property"],
                    measure=row["measure"],
                    term=CERO[term[5:]] if is_cero else URIRef(term),
                    unit=row.get("unit", ""),
                    fit=row.get("fit") or ("exact" if is_cero else "extension"),
                    note=row.get("note", ""),
                )
                if _unit_type(entry.measure) and entry.unit not in UNITS:
                    raise ValueError(
                        f"{path}, line {line}: {entry.measure} needs a unit, one of "
                        f"{', '.join(UNITS)} (got '{entry.unit}')")
                mapping.append(entry)
    return mapping


def _find_mapping(mapping: List[PropertyMapping], element: ifcopenshell.entity_instance,
                  pset: str, name: str) -> Optional[PropertyMapping]:
    for entry in mapping:
        if (entry.ifc_name == name and fnmatch.fnmatchcase(pset, entry.pset)
                and entry.applies_to(element)):
            return entry
    return None


def _rdf_value(value, measure: str, mapping: PropertyMapping, ifc_file: ifcopenshell.file):
    """Stored IFC value -> value in the unit of the RDF property."""
    if not isinstance(value, float):
        return value
    return _round(value * _si_scale(ifc_file, measure) * mapping.si_to_rdf)


def _ifc_value(literal: Literal, mapping: PropertyMapping):
    """RDF literal -> value in SI base units, which is what cero_to_ifc writes."""
    value = literal.toPython()
    if mapping.measure in ("IfcBoolean", "IfcLogical"):
        return bool(value)
    if mapping.measure == "IfcInteger":
        return int(value)
    if mapping.measure in ("IfcIdentifier", "IfcLabel", "IfcText"):
        return str(value)
    return _round(float(value) / mapping.si_to_rdf)


# ── Report ───────────────────────────────────────────────────────────────────

@dataclass
class ConversionReport:
    """What a conversion did, and what it could not map."""
    elements: Counter = field(default_factory=Counter)      # IFC class -> count
    terms: Counter = field(default_factory=Counter)         # RDF term -> triples
    unmapped: Counter = field(default_factory=Counter)      # set.property -> count
    skipped: Counter = field(default_factory=Counter)       # reason -> count
    without_geometry: int = 0

    def update(self, other: "ConversionReport"):
        for name in ("elements", "terms", "unmapped", "skipped"):
            getattr(self, name).update(getattr(other, name))
        self.without_geometry += other.without_geometry

    def summary(self, max_unmapped: int = 20) -> str:
        lines = [f"  Elements: {dict(self.elements)}"]
        cero = sorted(str(t)[len(str(CERO)):] for t in self.terms if str(t).startswith(str(CERO)))
        if cero:
            lines.append(f"  CERO properties used ({len(cero)}): {', '.join(cero)}")
        other = sum(1 for t in self.terms if not str(t).startswith(str(CERO)))
        if other:
            lines.append(f"  Properties from other namespaces used: {other}")
        if self.unmapped:
            shown = ", ".join(f"{n} ({c})" for n, c in self.unmapped.most_common(max_unmapped))
            more = len(self.unmapped) - max_unmapped
            lines.append(f"  Unmapped IFC properties (dropped): {shown}"
                         + (f", and {more} more" if more > 0 else ""))
        if self.skipped:
            lines.append(f"  Skipped: {dict(self.skipped)}")
        if self.without_geometry:
            lines.append(f"  Elements without geometry: {self.without_geometry}")
        return "\n".join(lines)


# ── IFC -> CERO ──────────────────────────────────────────────────────────────

def _read_properties(element: ifcopenshell.entity_instance) -> Dict[Tuple[str, str], Tuple[object, str]]:
    """
    Collect single-value properties and simple quantities of an element as
    (set, name) -> (value, IFC type). Values of the element itself take
    precedence over values of its element type.
    """
    definitions = [rel.RelatingPropertyDefinition for rel in element.IsDefinedBy
                   if rel.is_a("IfcRelDefinesByProperties")]
    element_type = ifcopenshell.util.element.get_type(element)
    if element_type is not None:
        definitions += element_type.HasPropertySets or ()

    props: Dict[Tuple[str, str], Tuple[object, str]] = {}
    for definition in definitions:
        if definition.is_a("IfcPropertySet"):
            for prop in definition.HasProperties:
                if prop.is_a("IfcPropertySingleValue") and prop.NominalValue is not None:
                    props.setdefault((definition.Name, prop.Name),
                                     (prop.NominalValue.wrappedValue, prop.NominalValue.is_a()))
        elif definition.is_a("IfcElementQuantity"):
            for quantity in definition.Quantities:
                # The value is the fourth attribute of every simple quantity
                if quantity.is_a("IfcPhysicalSimpleQuantity") and quantity[3] is not None:
                    props.setdefault((definition.Name, quantity.Name),
                                     (quantity[3], quantity.is_a()))
    return props


def _elements(ifc_file: ifcopenshell.file, classes: Sequence[str]) -> Iterator[ifcopenshell.entity_instance]:
    seen = set()
    for ifc_class in classes:
        try:
            found = ifc_file.by_type(ifc_class)
        except RuntimeError:
            # Class is not part of the schema of this file
            continue
        for element in found:
            # In IFC2X3, reinforcement and element parts are building elements too.
            # They are only converted when their class is asked for.
            if ifc_class in DEFAULT_CLASSES and element.is_a("IfcBuildingElementComponent"):
                continue
            if element.id() not in seen:
                seen.add(element.id())
                yield element


def _element_type(element: ifcopenshell.entity_instance) -> str:
    """Readable element type, e.g. 'Slab (FLOOR)'. Read back by cero_to_ifc."""
    text = element.is_a()[3:]
    predefined = getattr(element, "PredefinedType", None)
    if predefined and predefined not in ("NOTDEFINED", "USERDEFINED"):
        text += f" ({predefined})"
    return text


def _new_graph(mapping: List[PropertyMapping]) -> Graph:
    graph = Graph()
    for prefix, ns in (("cero", CERO), ("bot", BOT), ("ifc", IFCOWL), ("fog", FOG)):
        graph.bind(prefix, ns)
    for index, ns in enumerate(_extension_namespaces(mapping)):
        graph.bind("ext" if index == 0 else f"ext{index + 1}", Namespace(ns))
    return graph


def _namespace_of(term: URIRef) -> str:
    return re.match(r".*[#/]", str(term)).group(0)


def _extension_namespaces(mapping: List[PropertyMapping]) -> List[str]:
    """Namespaces of the mapped terms that are not CERO terms, in mapping order."""
    namespaces = dict.fromkeys(_namespace_of(m.term) for m in mapping)
    namespaces.pop(str(CERO), None)
    return list(namespaces)


def _node(ns: Namespace, obj: ifcopenshell.entity_instance) -> URIRef:
    return ns[quote(obj.GlobalId, safe="")]


def _mesh_obj(settings, element: ifcopenshell.entity_instance) -> Optional[str]:
    """Tessellate an element in world coordinates as OBJ text (m)."""
    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
    except Exception:
        return None
    verts, faces = shape.geometry.verts, shape.geometry.faces
    lines = []
    for i in range(0, len(verts), 3):
        # ifcopenshell.geom returns metres; + 0.0 turns -0.0 into 0.0
        x, y, z = (round(c, 5) + 0.0 for c in verts[i:i + 3])
        lines.append(f"v {x:.5f} {y:.5f} {z:.5f}")
    for i in range(0, len(faces), 3):
        lines.append(f"f {faces[i] + 1} {faces[i + 1] + 1} {faces[i + 2] + 1}")
    return "\n".join(lines) if lines else None


def _add_spatial_structure(graph: Graph, ns: Namespace, ifc_file: ifcopenshell.file):
    """Describe buildings and storeys with BOT. CERO has no spatial structure."""
    for ifc_class, bot_class in (("IfcBuilding", BOT.Building), ("IfcBuildingStorey", BOT.Storey)):
        for zone in ifc_file.by_type(ifc_class):
            node = _node(ns, zone)
            graph.add((node, RDF.type, bot_class))
            graph.add((node, DCTERMS.identifier, Literal(zone.GlobalId)))
            if zone.Name:
                graph.add((node, RDFS.label, Literal(zone.Name)))
            parent = ifcopenshell.util.element.get_aggregate(zone)
            if bot_class == BOT.Storey and parent is not None and parent.is_a("IfcBuilding"):
                graph.add((_node(ns, parent), BOT.hasStorey, node))


def ifc_to_cero(
    ifc_path: str,
    mapping: Optional[List[PropertyMapping]] = None,
    base_iri: str = DEFAULT_BASE_IRI,
    dataset_name: Optional[str] = None,
    classes: Sequence[str] = DEFAULT_CLASSES,
    geometry: bool = False,
) -> Tuple[Graph, ConversionReport]:
    """
    Convert the elements of an IFC file to a CERO graph.

    Values are converted from the units declared in the IFC file to the unit
    given in the mapping. IFC properties without a mapping are dropped and
    listed in the report.

    Args:
        ifc_path: Path to the IFC file
        mapping: Result of load_mapping() (default: mapping_ifc4.csv)
        base_iri: Base IRI under which the dataset and its elements are minted
        dataset_name: Name of the dataset (default: file name without extension)
        classes: IFC classes to convert, including their subclasses
        geometry: Also store each element's tessellated geometry in world
            coordinates (fog:asObj_v3.0-obj, in m)

    Returns:
        (graph, report)
    """
    mapping = load_mapping() if mapping is None else mapping
    ifc_file = ifcopenshell.open(str(ifc_path))
    dataset_name = dataset_name or Path(ifc_path).stem
    dataset = URIRef(f"{base_iri}{quote(dataset_name)}")
    ns = Namespace(f"{dataset}#")

    graph = _new_graph(mapping)
    graph.bind("data", ns)
    graph.add((dataset, RDF.type, OWL.Ontology))
    graph.add((dataset, OWL.imports, CERO_ONTOLOGY))
    graph.add((dataset, DCTERMS.source, Literal(Path(ifc_path).name)))
    project = ifc_file.by_type("IfcProject")[0]
    if project.Name:
        graph.add((dataset, RDFS.label, Literal(project.Name)))
    if project.Description:
        graph.add((dataset, RDFS.comment, Literal(project.Description)))

    _add_spatial_structure(graph, ns, ifc_file)
    if geometry:
        settings = ifcopenshell.geom.settings()
        settings.set("use-world-coords", True)

    report = ConversionReport()
    for element in _elements(ifc_file, classes):
        report.elements[element.is_a()] += 1

        subject = _node(ns, element)
        graph.add((subject, RDF.type, BOT.Element))
        graph.add((subject, RDF.type, IFCOWL[element.is_a()]))
        graph.add((subject, CERO.identifier, Literal(element.GlobalId)))
        report.terms[CERO.identifier] += 1
        if element.Name:
            graph.add((subject, RDFS.label, Literal(element.Name)))
        if element.Description:
            graph.add((subject, RDFS.comment, Literal(element.Description)))

        for (pset, name), (value, measure) in _read_properties(element).items():
            entry = _find_mapping(mapping, element, pset, name)
            if entry is None:
                report.unmapped[f"{pset}.{name}"] += 1
                continue
            if (subject, entry.term, None) in graph:
                # An earlier property already filled this term
                report.skipped[f"second value for {entry.term}"] += 1
                continue
            graph.add((subject, entry.term, _literal(_rdf_value(value, measure, entry, ifc_file))))
            report.terms[entry.term] += 1

        if (subject, CERO.elementType, None) not in graph:
            graph.add((subject, CERO.elementType, Literal(_element_type(element))))
            report.terms[CERO.elementType] += 1

        container = ifcopenshell.util.element.get_container(element)
        if container is not None and container.is_a() in ("IfcBuilding", "IfcBuildingStorey"):
            graph.add((_node(ns, container), BOT.containsElement, subject))

        if geometry:
            mesh = _mesh_obj(settings, element)
            if mesh:
                graph.add((subject, GEOMETRY, Literal(mesh)))
            else:
                report.without_geometry += 1

    return graph, report


# ── CERO -> IFC ──────────────────────────────────────────────────────────────

def _ifc_class_from_graph(graph: Graph, subject: URIRef) -> str:
    """IFC class from the ifcOWL type. Plain CERO data becomes a proxy element."""
    schema = ifcopenshell.schema_by_name(OUTPUT_SCHEMA)
    for rdf_type in graph.objects(subject, RDF.type):
        if not str(rdf_type).startswith(str(IFCOWL)):
            continue
        name = str(rdf_type)[len(str(IFCOWL)):]
        try:
            schema.declaration_by_name(name)
        except RuntimeError:
            continue
        return name
    return "IfcBuildingElementProxy"


def _set_name(pattern: str, ifc_class: str) -> str:
    """Resolve a set name pattern for a class: Qto_*BaseQuantities -> Qto_BeamBaseQuantities."""
    if "*" not in pattern:
        return pattern
    template = ifcopenshell.util.pset.get_template(OUTPUT_SCHEMA)
    names = [n for n in template.get_applicable_names(ifc_class, schema=OUTPUT_SCHEMA)
             if fnmatch.fnmatchcase(n, pattern)]
    return min(names, key=len) if names else pattern.replace("*", ifc_class[3:])


def _mesh_geometry(ifc_file, body_context, obj: str):
    """Triangulated face set from OBJ text (m, world coordinates)."""
    coords, index = [], []
    for line in obj.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "v":
            coords.append(tuple(float(c) for c in parts[1:4]))
        elif parts[0] == "f":
            # Only the vertex index of v/vt/vn
            index.append(tuple(int(i.split("/")[0]) for i in parts[1:4]))
    if not coords or not index:
        return None
    points = ifc_file.create_entity('IfcCartesianPointList3D', CoordList=coords)
    face_set = ifc_file.create_entity('IfcTriangulatedFaceSet', Coordinates=points,
                                      CoordIndex=index)
    shape_rep = ifc_file.create_entity('IfcShapeRepresentation',
        ContextOfItems=body_context, RepresentationIdentifier='Body',
        RepresentationType='Tessellation', Items=[face_set])
    return ifc_file.create_entity('IfcProductDefinitionShape', Representations=[shape_rep])


def _box_geometry(ifc_file, body_context, length: float, width: float, height: float):
    """Placeholder box of length x width x height (m), centred on its footprint."""
    profile = ifc_file.create_entity('IfcRectangleProfileDef',
        ProfileType='AREA', XDim=length, YDim=width)
    direction = ifc_file.create_entity('IfcDirection', DirectionRatios=(0.0, 0.0, 1.0))
    solid = ifc_file.create_entity('IfcExtrudedAreaSolid',
        SweptArea=profile, ExtrudedDirection=direction, Depth=height)
    shape_rep = ifc_file.create_entity('IfcShapeRepresentation',
        ContextOfItems=body_context, RepresentationIdentifier='Body',
        RepresentationType='SweptSolid', Items=[solid])
    return ifc_file.create_entity('IfcProductDefinitionShape', Representations=[shape_rep])


def _write_property_sets(ifc_file, element, items: Dict[Tuple[str, bool], list]):
    """Attach properties and quantities to an element, grouped into their sets."""
    for (name, is_quantity), entries in items.items():
        if is_quantity:
            definition = ifc_file.create_entity('IfcElementQuantity',
                GlobalId=ifcopenshell.guid.new(), Name=name, Quantities=entries)
        else:
            definition = ifc_file.create_entity('IfcPropertySet',
                GlobalId=ifcopenshell.guid.new(), Name=name, HasProperties=entries)
        ifc_file.create_entity('IfcRelDefinesByProperties',
            GlobalId=ifcopenshell.guid.new(), RelatedObjects=[element],
            RelatingPropertyDefinition=definition)


def _restore_identity(graph: Graph, node: URIRef, obj: ifcopenshell.entity_instance,
                      used_ids: set, identifier_term: URIRef):
    """Give an object back its name and, if it is a valid unused one, its GlobalId."""
    label = graph.value(node, RDFS.label)
    if label is not None:
        obj.Name = str(label)
    identifier = str(graph.value(node, identifier_term) or "")
    if len(identifier) == 22 and identifier not in used_ids:
        try:
            ifcopenshell.guid.expand(identifier)
        except Exception:
            return
        obj.GlobalId = identifier
    used_ids.add(obj.GlobalId)


def cero_to_ifc(graph: Graph, output_ifc: str,
                mapping: Optional[List[PropertyMapping]] = None) -> ConversionReport:
    """
    Write a CERO graph as an IFC4 file in SI base units (m, kg, N, Pa).

    Every bot:Element becomes an element of its ifcOWL class, or an
    IfcBuildingElementProxy if it has none. Mapped properties are written to
    the property and quantity sets named in the mapping. Buildings and storeys
    are restored from BOT.

    CERO carries neither geometry nor placement. Elements with a mesh
    (fog:asObj_v3.0-obj) get it back in world coordinates. Elements with
    cero:length, cero:width and cero:height get a placeholder box and are
    laid out in a row. All others have no geometry.

    Args:
        graph: Graph with bot:Element individuals described with CERO
        output_ifc: Path to output IFC file
        mapping: Result of load_mapping() (default: mapping_ifc4.csv)

    Returns:
        Conversion report
    """
    mapping = load_mapping() if mapping is None else mapping
    report = ConversionReport()

    dataset = next(iter(graph.subjects(RDF.type, OWL.Ontology)), None)
    project_name = graph.value(dataset, RDFS.label) if dataset is not None else None
    project_description = graph.value(dataset, RDFS.comment) if dataset is not None else None

    ifc_file = ifcopenshell.api.project.create_file(version=OUTPUT_SCHEMA)
    project = ifcopenshell.api.root.create_entity(
        ifc_file, ifc_class='IfcProject',
        name=str(project_name) if project_name is not None else 'CERO elements')
    if project_description is not None:
        project.Description = str(project_description)
    ifcopenshell.api.unit.assign_unit(ifc_file, units=[
        ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type=unit_type, prefix=prefix)
        for unit_type, prefix in (
            ('LENGTHUNIT', None), ('AREAUNIT', None), ('VOLUMEUNIT', None), ('MASSUNIT', 'KILO'),
            ('FORCEUNIT', None), ('PRESSUREUNIT', None), ('PLANEANGLEUNIT', None),
            ('TIMEUNIT', None))
    ])
    model_context = ifcopenshell.api.context.add_context(ifc_file, context_type='Model')
    body_context = ifcopenshell.api.context.add_context(
        ifc_file, context_type='Model', context_identifier='Body',
        target_view='MODEL_VIEW', parent=model_context)

    # Spatial structure
    used_ids: set = set()
    zones: Dict[URIRef, ifcopenshell.entity_instance] = {}
    fallback: Dict[str, ifcopenshell.entity_instance] = {}
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class='IfcSite', name='Site')
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[site], relating_object=project)

    def add_zone(node, ifc_class, parent, name=None):
        zone = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=ifc_class, name=name)
        ifcopenshell.api.aggregate.assign_object(ifc_file, products=[zone], relating_object=parent)
        if node is not None:
            _restore_identity(graph, node, zone, used_ids, DCTERMS.identifier)
            zones[node] = zone
        return zone

    def fallback_building():
        if 'building' not in fallback:
            fallback['building'] = next(
                (z for z in zones.values() if z.is_a('IfcBuilding')), None
            ) or add_zone(None, 'IfcBuilding', site, 'Building')
        return fallback['building']

    def fallback_storey():
        if 'storey' not in fallback:
            fallback['storey'] = add_zone(None, 'IfcBuildingStorey', fallback_building(),
                                          'CERO elements')
        return fallback['storey']

    for node in sorted(set(graph.subjects(RDF.type, BOT.Building))):
        building = add_zone(node, 'IfcBuilding', site)
        for storey_node in sorted(graph.objects(node, BOT.hasStorey)):
            add_zone(storey_node, 'IfcBuildingStorey', building)
    for node in sorted(set(graph.subjects(RDF.type, BOT.Storey))):
        if node not in zones:
            add_zone(node, 'IfcBuildingStorey', fallback_building())

    # Elements
    contents: Dict[ifcopenshell.entity_instance, list] = {}
    set_names: Dict[Tuple[str, str], str] = {}
    row_y = 0.0
    for subject in sorted(set(graph.subjects(RDF.type, BOT.Element))):
        ifc_class = _ifc_class_from_graph(graph, subject)
        element = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=ifc_class)
        _restore_identity(graph, subject, element, used_ids, CERO.identifier)
        comment = graph.value(subject, RDFS.comment)
        if comment is not None:
            element.Description = str(comment)
        predefined = re.search(r"\(([A-Z_]+)\)$", str(graph.value(subject, CERO.elementType) or ""))
        if predefined and hasattr(element, 'PredefinedType'):
            try:
                element.PredefinedType = predefined.group(1)
            except Exception:
                # Not a predefined type of this class
                pass

        items: Dict[Tuple[str, bool], list] = {}
        written = set()
        for entry in mapping:
            if entry.term in written or not entry.applies_to(element):
                continue
            literal = graph.value(subject, entry.term)
            if literal is None:
                continue
            written.add(entry.term)
            value = _ifc_value(literal, entry)
            if entry.is_quantity:
                item = ifc_file.create_entity(entry.measure, Name=entry.ifc_name)
                item[3] = value
            else:
                item = ifc_file.create_entity('IfcPropertySingleValue', Name=entry.ifc_name,
                    NominalValue=ifc_file.create_entity(entry.measure, value))
            key = (entry.pset, ifc_class)
            if key not in set_names:
                set_names[key] = _set_name(*key)
            items.setdefault((set_names[key], entry.is_quantity), []).append(item)
        _write_property_sets(ifc_file, element, items)

        mesh = graph.value(subject, GEOMETRY)
        dimensions = [graph.value(subject, term) for term in (CERO.length, CERO.width, CERO.height)]
        position = (0.0, 0.0, 0.0)
        shape = None
        if mesh is not None:
            # Mesh is in world coordinates
            shape = _mesh_geometry(ifc_file, body_context, str(mesh))
        elif all(d is not None and float(d) > 0 for d in dimensions):
            length, width, height = (float(d) for d in dimensions)
            shape = _box_geometry(ifc_file, body_context, length, width, height)
            position = (length / 2, row_y + width / 2, 0.0)
            row_y += width + 1.0
        if shape is None:
            report.without_geometry += 1
        element.Representation = shape
        origin = ifc_file.create_entity('IfcCartesianPoint', Coordinates=position)
        placement = ifc_file.create_entity('IfcAxis2Placement3D', Location=origin)
        element.ObjectPlacement = ifc_file.create_entity('IfcLocalPlacement',
                                                         RelativePlacement=placement)

        containers = [zones[n] for n in graph.subjects(BOT.containsElement, subject) if n in zones]
        # A storey is more specific than its building
        containers.sort(key=lambda zone: not zone.is_a('IfcBuildingStorey'))
        contents.setdefault(containers[0] if containers else fallback_storey(), []).append(element)
        report.elements[ifc_class] += 1

    for container, elements in contents.items():
        ifcopenshell.api.spatial.assign_container(ifc_file, products=elements,
                                                  relating_structure=container)

    Path(output_ifc).parent.mkdir(parents=True, exist_ok=True)
    ifc_file.write(str(output_ifc))
    return report


# ── Extension vocabulary ─────────────────────────────────────────────────────

def extension_vocabulary(mapping: List[PropertyMapping]) -> Graph:
    """
    Definitions of the mapped properties that are not CERO properties, written
    the way CERO defines its own (datatype property on bot:Element that is
    also an isoprops Property), so they can be proposed for inclusion in CERO.
    """
    graph = _new_graph(mapping)
    graph.bind("isoprops", ISOPROPS)
    for ns in _extension_namespaces(mapping):
        ontology = URIRef(ns.rstrip("#/"))
        graph.add((ontology, RDF.type, OWL.Ontology))
        graph.add((ontology, OWL.imports, CERO_ONTOLOGY))

    ranges = {"IfcBoolean": XSD.boolean, "IfcLogical": XSD.boolean, "IfcInteger": XSD.integer,
              "IfcIdentifier": XSD.string, "IfcLabel": XSD.string, "IfcText": XSD.string}
    for entry in mapping:
        term = entry.term
        if str(term).startswith(str(CERO)) or (term, RDF.type, None) in graph:
            continue
        name = str(term)[len(_namespace_of(term)):]
        label = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name).lower()
        graph.add((term, RDF.type, OWL.DatatypeProperty))
        graph.add((term, RDF.type, ISOPROPS.Property))
        graph.add((term, RDFS.domain, BOT.Element))
        graph.add((term, RDFS.range, ranges.get(entry.measure, XSD.decimal)))
        graph.add((term, RDFS.label, Literal(label, lang="en")))
        comment = "; ".join(p for p in (f"Unit: {entry.unit}" if entry.unit else "", entry.note) if p)
        if comment:
            graph.add((term, RDFS.comment, Literal(comment, lang="en")))
        if entry.unit in UNITS:
            graph.add((term, ISOPROPS.hasUnit, QUDT_UNIT[UNITS[entry.unit][1]]))
    return graph


# ── Round trip check ─────────────────────────────────────────────────────────

def _vertices(mesh: str) -> set:
    return {line for line in mesh.splitlines() if line.startswith("v ")}


def _short(graph: Graph, term: URIRef) -> str:
    try:
        return graph.namespace_manager.curie(term)
    except Exception:
        return str(term)


def verify_roundtrip(
    ifc_path: str,
    mapping: Optional[List[PropertyMapping]] = None,
    classes: Sequence[str] = DEFAULT_CLASSES,
    geometry: bool = False,
) -> List[str]:
    """
    Check IFC -> CERO -> Turtle -> CERO -> IFC -> CERO.

    The graph of the rebuilt IFC file must equal the graph of the original
    file. Comparing graphs rather than raw IFC values makes the check
    independent of the units the original file was stored in. Meshes are
    compared by their vertex sets, since triangulation order may change.

    Returns:
        List of differences (empty if the round trip is lossless for all
        mapped properties)
    """
    mapping = load_mapping() if mapping is None else mapping
    name = Path(ifc_path).stem
    original, _ = ifc_to_cero(ifc_path, mapping, dataset_name=name, classes=classes,
                              geometry=geometry)
    parsed = Graph().parse(data=original.serialize(format="turtle"), format="turtle")

    with tempfile.TemporaryDirectory() as tmp:
        rebuilt_ifc = str(Path(tmp) / f"{name}.ifc")
        cero_to_ifc(parsed, rebuilt_ifc, mapping)
        rebuilt, _ = ifc_to_cero(rebuilt_ifc, mapping, dataset_name=name, classes=classes,
                                 geometry=geometry)

    differences = []
    for label, a, b in (("lost", original, rebuilt), ("added", rebuilt, original)):
        for s, p, o in a:
            if p == DCTERMS.source:
                continue
            if p == GEOMETRY:
                other = b.value(s, p)
                # Placeholder boxes of the rebuilt file are not a difference
                if (label == "lost" or other is not None) and (
                        other is None or _vertices(str(o)) != _vertices(str(other))):
                    differences.append(f"{label}: {s.split('#')[-1]} geometry differs")
            elif (s, p, o) not in b:
                differences.append(f"{label}: {s.split('#')[-1]} {_short(a, p)} {o}")
    return sorted(differences)


# ── CLI ──────────────────────────────────────────────────────────────────────

def _add_mapping_argument(parser: argparse.ArgumentParser):
    parser.add_argument('--mapping', '-m', nargs='+', type=Path, default=[DEFAULT_MAPPING],
                        help='Mapping tables (CSV); earlier files take precedence '
                             f'(default: {DEFAULT_MAPPING.name})')


def _add_conversion_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('input', nargs='+', type=Path, help='IFC files')
    _add_mapping_argument(parser)
    parser.add_argument('--classes', nargs='+', default=list(DEFAULT_CLASSES),
                        help='IFC classes to convert, including their subclasses '
                             '(default: all building elements)')
    parser.add_argument('--geometry', action='store_true',
                        help='Also convert the tessellated geometry of each element')


def main():
    parser = argparse.ArgumentParser(description='Convert building elements between IFC and CERO')
    sub = parser.add_subparsers(dest='command', required=True)

    to_cero = sub.add_parser('to-cero', help='IFC -> CERO (Turtle)')
    _add_conversion_arguments(to_cero)
    to_cero.add_argument('--output-dir', '-o', type=Path, default=Path('.'),
                         help='Output directory (default: current directory)')
    to_cero.add_argument('--base-iri', type=str, default=DEFAULT_BASE_IRI,
                         help='Base IRI for datasets and elements')

    to_ifc = sub.add_parser('to-ifc', help='CERO (Turtle) -> IFC')
    to_ifc.add_argument('input', type=Path, help='Turtle file')
    to_ifc.add_argument('--output', '-o', type=Path, required=True, help='Path to output IFC file')
    _add_mapping_argument(to_ifc)

    roundtrip = sub.add_parser('roundtrip', help='Check that IFC -> CERO -> IFC is lossless')
    _add_conversion_arguments(roundtrip)

    vocabulary = sub.add_parser(
        'vocabulary', help='Write definitions of the mapped properties that are not in CERO')
    _add_mapping_argument(vocabulary)
    vocabulary.add_argument('--output', '-o', type=Path, required=True,
                            help='Path to output Turtle file')

    args = parser.parse_args()
    mapping = load_mapping(args.mapping)

    if args.command == 'vocabulary':
        graph = extension_vocabulary(mapping)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(destination=str(args.output), format="turtle")
        print(f"[OK] Extension vocabulary: {args.output} ({len(graph)} triples)")
        return 0

    if args.command == 'to-ifc':
        report = cero_to_ifc(Graph().parse(str(args.input)), str(args.output), mapping)
        print(f"[OK] Created IFC file: {args.output}")
        print(report.summary())
        return 0

    if args.command == 'to-cero':
        args.output_dir.mkdir(parents=True, exist_ok=True)
        total = ConversionReport()
        for ifc_path in args.input:
            graph, report = ifc_to_cero(str(ifc_path), mapping, base_iri=args.base_iri,
                                        classes=args.classes, geometry=args.geometry)
            output = args.output_dir / f"{ifc_path.stem}.ttl"
            graph.serialize(destination=str(output), format="turtle")
            total.update(report)
            if len(args.input) <= 10:
                print(f"[OK] {ifc_path.name} -> {output} ({len(graph)} triples)")
                print(report.summary())
        if len(args.input) > 10:
            print(f"[OK] {len(args.input)} files -> {args.output_dir}")
            print(total.summary())
        return 0

    failed = 0
    for ifc_path in args.input:
        differences = verify_roundtrip(str(ifc_path), mapping, classes=args.classes,
                                       geometry=args.geometry)
        if differences:
            failed += 1
            print(f"[FAIL] {ifc_path.name}: {len(differences)} differences")
            for line in differences[:10]:
                print(f"  {line}")
        else:
            print(f"[OK] {ifc_path.name}: round trip is lossless for all mapped properties")
    return 1 if failed else 0


if __name__ == '__main__':
    exit(main())

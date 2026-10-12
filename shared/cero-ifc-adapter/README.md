# CERO <-> IFC adapter

Converts the building elements of an IFC file to RDF using the
[Concrete Element Reuse Ontology](../../cero/) (CERO, <https://w3id.org/cero>)
and back.

* [cero_ifc.py](cero_ifc.py): the adapter (command line tool and Python module)
* [mapping_ifc4.csv](mapping_ifc4.csv): default mapping of standard IFC property and quantity sets to CERO
* [mapping_example.csv](mapping_example.csv): example mapping of project-specific property sets
* [test_cero_ifc.py](test_cero_ifc.py): tests

## Usage

Requires Python 3.10 or later, `ifcopenshell>=0.8` and `rdflib>=7`. With
[uv](https://docs.astral.sh/uv/), the dependencies are installed on the fly:

```
uv run cero_ifc.py to-cero model.ifc -o out/                 # IFC -> CERO (Turtle)
uv run cero_ifc.py to-ifc out/model.ttl -o model_cero.ifc    # CERO -> IFC
uv run cero_ifc.py roundtrip model.ifc                       # check IFC -> CERO -> IFC
uv run cero_ifc.py vocabulary -m my_psets.csv -o my_ext.ttl  # define non-CERO properties
```

Otherwise `pip install ifcopenshell rdflib` and run it with `python`.

| Option | Commands | Meaning |
|---|---|---|
| `--mapping`, `-m` | all | One or more mapping tables. Earlier tables take precedence. Default: `mapping_ifc4.csv` |
| `--classes` | `to-cero`, `roundtrip` | IFC classes to convert, including their subclasses. Default: all building elements |
| `--geometry` | `to-cero`, `roundtrip` | Also convert the tessellated geometry of each element |
| `--base-iri` | `to-cero` | Base IRI of the dataset and its elements. The default is an `example.org` placeholder |

As a module:

```python
import cero_ifc

mapping = cero_ifc.load_mapping(["my_psets.csv", cero_ifc.DEFAULT_MAPPING])
graph, report = cero_ifc.ifc_to_cero("model.ifc", mapping, base_iri="https://example.org/stock/")
print(report.summary())
graph.serialize("model.ttl", format="turtle")

cero_ifc.cero_to_ifc(graph, "model_cero.ifc", mapping)
```

## How elements are represented

CERO v0.1 is a flat property dictionary: datatype properties with domain
`bot:Element`, no element classes and no object properties. The adapter
therefore describes each IFC element as one `bot:Element` individual:

```turtle
data:2O2Fr%24t4X7Zf8NOew3FLOH a bot:Element, ifc:IfcBeam ;
    rdfs:label "B1" ;
    cero:identifier "2O2Fr$t4X7Zf8NOew3FLOH" ;
    cero:elementType "Beam" ;
    cero:length 6.0 ;
    cero:volume 0.72 ;
    cero:concreteCover 30.0 ;
    cero:exposureClass "XC1" .

data:1hOSvn6df7F8_7GcBWlRGQ a bot:Storey ;
    bot:containsElement data:2O2Fr%24t4X7Zf8NOew3FLOH .
```

| RDF | Source in IFC | Direction |
|---|---|---|
| `rdf:type` | `bot:Element`, plus the IFC class as ifcOWL class | two-way |
| `cero:identifier` | GlobalId | two-way |
| `rdfs:label`, `rdfs:comment` | Name, Description | two-way |
| `cero:elementType` | class and predefined type, e.g. `Slab (FLOOR)`, unless a mapping row fills it | two-way |
| mapped properties | property sets and quantity sets, see below | two-way |
| `bot:Building`, `bot:Storey`, `bot:hasStorey`, `bot:containsElement` | spatial structure | two-way |
| `fog:asObj_v3.0-obj` | with `--geometry`: mesh in world coordinates, OBJ syntax, in m | two-way, as mesh |

Values are converted from the units declared in the IFC file to the unit of
the mapping row, which for CERO properties is the unit CERO declares.

## Mapping tables

Which IFC property fills which RDF property is defined in CSV tables, not in
code. One row maps one single-value property or one simple quantity:

| Column | Meaning |
|---|---|
| `ifc_class` | IFC class the row applies to, including its subclasses, or `*` |
| `pset` | Property set or quantity set. May contain `*`, e.g. `Pset_*Common` |
| `property` | Name of the property or quantity |
| `measure` | IFC value type (`IfcLengthMeasure`, `IfcLabel`, ...) or quantity class (`IfcQuantityLength`, ...) used when writing IFC |
| `term` | `cero:<name>`, or the full IRI of a property in another namespace |
| `unit` | Unit of the RDF value: `m`, `mm`, `m2`, `mm2`, `m3`, `kg`, `t`, `kN`, `kNm`, `MPa`, `GPa`, ... (see `UNITS` in the adapter). Required for dimensional types |
| `fit` | `exact` (same quantity), `close` (nearest CERO property, see note) or `extension` (no CERO counterpart) |
| `note` | Free text |

The first matching row wins. If two properties of one element map to the same
term, the first one found is kept. When writing IFC, a term goes to the first
row that applies to the element's class; a `*` in the set name is resolved to
the standard set of that class (`Qto_*BaseQuantities` becomes
`Qto_BeamBaseQuantities` for a beam).

IFC properties without a row are dropped and listed in the conversion report,
which shows what a project-specific table still has to cover.

### Default mapping

[mapping_ifc4.csv](mapping_ifc4.csv) covers the buildingSMART property and
quantity sets that have a counterpart in CERO:

| IFC | CERO | Unit | Fit |
|---|---|---|---|
| `Qto_*BaseQuantities.Length` | `cero:length` | m | exact |
| `Qto_*BaseQuantities.Width` | `cero:width` | m | exact |
| `Qto_*BaseQuantities.Height` | `cero:height` | m | exact |
| `Qto_SlabBaseQuantities.Depth` | `cero:height` | m | close |
| `Qto_*BaseQuantities.NetVolume` | `cero:volume` | m3 | exact |
| `Qto_*BaseQuantities.NetWeight` | `cero:weight` | kg | exact |
| `Pset_ConcreteElementGeneral.ConcreteCover` | `cero:concreteCover` | mm | exact |
| `Pset_ConcreteElementGeneral.ExposureClass` | `cero:exposureClass` | | exact |
| `Pset_BeamCommon.Span` | `cero:length` | m | close |

CERO declares no unit for `width`, `volume` and `weight`; m, m3 and kg are
assumed. Most CERO properties (condition, durability, provenance, lifecycle)
have no counterpart in the standard IFC property sets and stay empty unless a
project-specific table fills them.

### Project-specific property sets and extension properties

Real models mostly carry their data in their own property sets.
[mapping_example.csv](mapping_example.csv) shows both cases:

* a custom property that fits a CERO property
  (`Structural.Concrete_fck` to `cero:compressiveStrength`, in MPa)
* a custom property without a CERO counterpart, kept under a namespace of
  your own so that it survives the round trip
  (`Structural.MomentResistance_MRd` to `https://example.org/reuse#momentResistance`, in kNm)

```
uv run cero_ifc.py to-cero model.ifc -m mapping_example.csv mapping_ifc4.csv
```

The `vocabulary` command writes definitions for the properties that are not
CERO properties, in the way CERO defines its own (datatype property on
`bot:Element` that is also an `isoprops:Property`, with a QUDT unit). This is
a starting point for proposing them for inclusion in CERO.
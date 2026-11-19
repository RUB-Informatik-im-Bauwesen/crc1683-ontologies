"""
Tests for the CERO <-> IFC adapter.

    pytest shared/cero-ifc-adapter
"""

from decimal import Decimal
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.guid
import ifcopenshell.util.element
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF

import cero_ifc
from cero_ifc import BOT, CERO, IFCOWL

HERE = Path(__file__).parent
ONTOLOGY = HERE.parent.parent / "cero" / "ontology.ttl"
EXAMPLE_MAPPING = HERE / "mapping_example.csv"
EXT = "https://example.org/reuse#"


def _add_set(ifc_file, element, name, properties=(), quantities=()):
    if quantities:
        items = []
        for quantity_class, quantity_name, value in quantities:
            item = ifc_file.create_entity(quantity_class, Name=quantity_name)
            item[3] = value
            items.append(item)
        definition = ifc_file.create_entity('IfcElementQuantity',
            GlobalId=ifcopenshell.guid.new(), Name=name, Quantities=items)
    else:
        definition = ifc_file.create_entity('IfcPropertySet',
            GlobalId=ifcopenshell.guid.new(), Name=name, HasProperties=[
                ifc_file.create_entity('IfcPropertySingleValue', Name=property_name,
                    NominalValue=ifc_file.create_entity(measure, value))
                for measure, property_name, value in properties])
    ifc_file.create_entity('IfcRelDefinesByProperties', GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[element], RelatingPropertyDefinition=definition)


@pytest.fixture
def model(tmp_path):
    """A beam and a floor slab in one storey, stored in mm, kN and MPa."""
    ifc_file = ifcopenshell.api.project.create_file(version='IFC4')
    project = ifcopenshell.api.root.create_entity(ifc_file, ifc_class='IfcProject', name='Stock')
    ifcopenshell.api.unit.assign_unit(ifc_file, units=[
        ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type='LENGTHUNIT', prefix='MILLI'),
        ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type='VOLUMEUNIT'),
        ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type='MASSUNIT', prefix='KILO'),
        ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type='FORCEUNIT', prefix='KILO'),
        ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type='PRESSUREUNIT', prefix='MEGA'),
    ])
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class='IfcBuilding', name='Donor')
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class='IfcBuildingStorey', name='L1')
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[building], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[storey], relating_object=building)

    beam = ifcopenshell.api.root.create_entity(ifc_file, ifc_class='IfcBeam', name='B1')
    _add_set(ifc_file, beam, 'Qto_BeamBaseQuantities', quantities=[
        ('IfcQuantityLength', 'Length', 6000.0), ('IfcQuantityVolume', 'NetVolume', 0.72),
        ('IfcQuantityWeight', 'NetWeight', 1800.0)])
    _add_set(ifc_file, beam, 'Pset_ConcreteElementGeneral', properties=[
        ('IfcPositiveLengthMeasure', 'ConcreteCover', 30.0), ('IfcLabel', 'ExposureClass', 'XC1')])
    _add_set(ifc_file, beam, 'Pset_BeamCommon', properties=[('IfcBoolean', 'LoadBearing', True)])
    _add_set(ifc_file, beam, 'Structural', properties=[
        ('IfcPressureMeasure', 'Concrete_fck', 30.0), ('IfcForceMeasure', 'ShearResistance_VRd', 212.5),
        ('IfcLabel', 'Remark', 'not mapped')])

    slab = ifcopenshell.api.root.create_entity(ifc_file, ifc_class='IfcSlab', name='S1',
                                               predefined_type='FLOOR')
    _add_set(ifc_file, slab, 'Qto_SlabBaseQuantities', quantities=[
        ('IfcQuantityLength', 'Length', 5000.0), ('IfcQuantityLength', 'Width', 1200.0),
        ('IfcQuantityLength', 'Depth', 200.0)])
    ifcopenshell.api.spatial.assign_container(ifc_file, products=[beam, slab],
                                              relating_structure=storey)

    path = tmp_path / "stock.ifc"
    ifc_file.write(str(path))
    return path, beam.GlobalId, slab.GlobalId


def _values(graph, global_id):
    subject = next(graph.subjects(CERO.identifier, Literal(global_id)))
    return {str(p): o.toPython() for p, o in graph.predicate_objects(subject)}


def test_mapped_cero_terms_exist():
    ontology = Graph().parse(str(ONTOLOGY))
    mapping = cero_ifc.load_mapping([cero_ifc.DEFAULT_MAPPING, EXAMPLE_MAPPING])
    terms = {m.term for m in mapping if str(m.term).startswith(str(CERO))}
    assert terms
    for term in terms:
        assert (term, RDF.type, OWL.DatatypeProperty) in ontology, term


def test_dimensional_measure_needs_unit(tmp_path):
    table = tmp_path / "mapping.csv"
    table.write_text("ifc_class,pset,property,measure,term,unit,fit,note\n"
                     "*,Dimensions,Span,IfcLengthMeasure,cero:length,,,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="needs a unit"):
        cero_ifc.load_mapping([table])


def test_ifc_to_cero_converts_units(model):
    path, beam_id, slab_id = model
    graph, report = cero_ifc.ifc_to_cero(str(path))

    beam = _values(graph, beam_id)
    assert beam[str(CERO.length)] == Decimal("6")
    assert beam[str(CERO.volume)] == Decimal("0.72")
    assert beam[str(CERO.weight)] == Decimal("1800")
    assert beam[str(CERO.concreteCover)] == Decimal("30")
    assert beam[str(CERO.exposureClass)] == "XC1"
    assert beam[str(CERO.elementType)] == "Beam"

    slab = _values(graph, slab_id)
    assert slab[str(CERO.height)] == Decimal("0.2")
    assert slab[str(CERO.elementType)] == "Slab (FLOOR)"

    assert report.elements == {"IfcBeam": 1, "IfcSlab": 1}
    assert report.unmapped["Structural.Remark"] == 1
    assert len(list(graph.subject_objects(BOT.containsElement))) == 2
    assert len(list(graph.subject_objects(BOT.hasStorey))) == 1


def test_custom_mapping_and_vocabulary(model):
    path, beam_id, _ = model
    mapping = cero_ifc.load_mapping([EXAMPLE_MAPPING, cero_ifc.DEFAULT_MAPPING])
    graph, _ = cero_ifc.ifc_to_cero(str(path), mapping)

    beam = _values(graph, beam_id)
    assert beam[str(CERO.compressiveStrength)] == Decimal("30")
    assert beam[EXT + "shearResistance"] == Decimal("212.5")
    assert beam[EXT + "loadBearing"] is True

    vocabulary = cero_ifc.extension_vocabulary(mapping)
    assert (URIRef(EXT + "shearResistance"), RDF.type, OWL.DatatypeProperty) in vocabulary
    assert (CERO.length, None, None) not in vocabulary


def test_cero_to_ifc(model, tmp_path):
    path, beam_id, slab_id = model
    mapping = cero_ifc.load_mapping([EXAMPLE_MAPPING, cero_ifc.DEFAULT_MAPPING])
    graph, _ = cero_ifc.ifc_to_cero(str(path), mapping)
    output = tmp_path / "rebuilt.ifc"
    cero_ifc.cero_to_ifc(graph, str(output), mapping)

    rebuilt = ifcopenshell.open(str(output))
    beam = rebuilt.by_guid(beam_id)
    slab = rebuilt.by_guid(slab_id)
    assert beam.is_a("IfcBeam") and beam.Name == "B1"
    assert slab.PredefinedType == "FLOOR"
    # Written in SI base units
    psets = ifcopenshell.util.element.get_psets(beam)
    # Two rows map to cero:length for beams; the first table decides where it is written
    assert psets["Dimensions"]["Span"] == pytest.approx(6.0)
    assert psets["Qto_BeamBaseQuantities"]["NetWeight"] == pytest.approx(1800.0)
    assert psets["Pset_ConcreteElementGeneral"]["ConcreteCover"] == pytest.approx(0.03)
    assert psets["Structural"]["Concrete_fck"] == pytest.approx(30e6)
    assert psets["Pset_BeamCommon"]["LoadBearing"] is True
    assert ifcopenshell.util.element.get_container(slab).Name == "L1"
    # The slab has length, width and height, so it gets a placeholder box
    assert slab.Representation is not None and beam.Representation is None


def test_plain_cero_data_becomes_proxy(tmp_path):
    graph = Graph().parse(format="turtle", data="""
        @prefix bot: <https://w3id.org/bot#> .
        @prefix cero: <https://w3id.org/cero#> .
        <https://example.org/stock#e1> a bot:Element ;
            cero:length 4.5 ; cero:concreteCover 25.0 .
    """)
    output = tmp_path / "plain.ifc"
    report = cero_ifc.cero_to_ifc(graph, str(output))
    assert report.elements == {"IfcBuildingElementProxy": 1}
    rebuilt = ifcopenshell.open(str(output))
    element = rebuilt.by_type("IfcBuildingElementProxy")[0]
    psets = ifcopenshell.util.element.get_psets(element)
    assert psets["Pset_ConcreteElementGeneral"]["ConcreteCover"] == pytest.approx(0.025)
    assert (None, RDF.type, IFCOWL.IfcBuildingElementProxy) not in graph


@pytest.mark.parametrize("tables", [
    [cero_ifc.DEFAULT_MAPPING],
    [EXAMPLE_MAPPING, cero_ifc.DEFAULT_MAPPING],
])
def test_roundtrip_is_lossless(model, tables):
    path, _, _ = model
    assert cero_ifc.verify_roundtrip(str(path), cero_ifc.load_mapping(tables)) == []

Markdown documentation created by [pyLODE](http://github.com/rdflib/pyLODE) 2.4

# Concrete Element Reuse Ontology (CERO)

## Metadata
* **IRI**
  * `https://w3id.org/cero`
* **Publisher(s)**
  * [Chair of Computing in Engineering, Ruhr University Bochum](https://www.inf.bi.rub.de)
* **Creators(s)**
  * [Lukas Guntermann](https://orcid.org/0009-0006-6615-6018)
    [[ORCID]](https://orcid.org/0009-0006-6615-6018)
    (<lukas.guntermann@rub.de></a>) of [Ruhr University Bochum](https://www.inf.bi.ruhr-uni-bochum.de/iib/lehrstuhl/mitarbeiter/lukas_guntermann.html.en)
  * [Nina Krautgartner](https://orcid.org/0009-0007-3836-1177)
    [[ORCID]](https://orcid.org/0009-0007-3836-1177)
    (<nina.krautgartner@rub.de></a>) of [Ruhr University Bochum](https://www.inf.bi.ruhr-uni-bochum.de/iib/lehrstuhl/mitarbeiter/nina_krautgartner.html.en)
  * [Philipp Hagedorn](https://orcid.org/0000-0002-6249-243X)
    [[ORCID]](https://orcid.org/0000-0002-6249-243X)
    (<philipp.hagedorn-n6v@rub.de></a>) of [Ruhr University Bochum](https://www.inf.bi.ruhr-uni-bochum.de/iib/lehrstuhl/mitarbeiter/philipp_hagedorn.html.en)
* **Created**
  * 2026-01-01
* **Modified**
  * 2025-01-15
* **Issued**
  * 2021-12-06
* **Version Information**
  * 0.1
* **Version IRI**
  * [https://w3id.org/cero](https://w3id.org/cero)
* **Imports**
  * [bot:](https://w3id.org/bot#)
  * [https://w3id.org/isoprops](https://w3id.org/isoprops)
  * [metadata4ing:](http://w3id.org/nfdi4ing/metadata4ing#)
* **License**
  * [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)
* **Ontology RDF**
  * RDF ([cero.ttl](turtle))
* **Code Repository**
  * [https://github.com/RUB-Informatik-im-Bauwesen/crc1683-ontologies/tree/main/cero](https://github.com/RUB-Informatik-im-Bauwesen/crc1683-ontologies/tree/main/cero)
### Description
<p>To be defined...</p>
* **History Note:** <p>v0.1: initial ontology</p>

## Table of Contents
1. [Classes](#classes)
1. [Datatype Properties](#datatypeproperties)
1. [Named Individuals](#namedindividuals)
1. [Namespaces](#namespaces)
1. [Legend](#legend)


## Overview

**Figure 1:** Ontology overview
## Classes
[Element](#Element),
[GroupOfProperties](#GroupOfProperties),
[NumericalVariable](#NumericalVariable),
[Property](#Property),
[Property](#Property1),
[TextVariable](#TextVariable),
[VariableSet](#VariableSet),
### NumericalVariable
Property | Value
--- | ---
IRI | `http://w3id.org/nfdi4ing/metadata4ing#NumericalVariable`
### TextVariable
Property | Value
--- | ---
IRI | `http://w3id.org/nfdi4ing/metadata4ing#TextVariable`
Super-classes |[isoprops:Property](https://w3id.org/isoprops#Property) (c)<br />
### VariableSet
Property | Value
--- | ---
IRI | `http://w3id.org/nfdi4ing/metadata4ing#VariableSet`
### Property
Property | Value
--- | ---
IRI | `http://www.molmod.info/semantics/pims-ii.ttl#Property`
### Element
Property | Value
--- | ---
IRI | `https://w3id.org/bot#Element`
In domain of |[cero:initialProject](Initialproject) (dp)<br />[cero:volume](Volume) (dp)<br />[cero:concreteStiffness](Concretestiffness) (dp)<br />[cero:connectionType](Connectiontype) (dp)<br />[cero:chlorideContent](Chloridecontent) (dp)<br />[cero:anchorPoints](Anchorpoints) (dp)<br />[cero:concreteCompressiveStrength](Concretecompressivestrength) (dp)<br />[cero:extraordinaryDamage](Extraordinarydamage) (dp)<br />[cero:transportDistance](Transportdistance) (dp)<br />[cero:weight](Weight) (dp)<br />[cero:elementType](elementtype) (dp)<br />[cero:origin](origin) (dp)<br />[cero:energyConsumed](Energyconsumed) (dp)<br />[cero:elementDimensions](elementdimensions) (dp)<br />[cero:density](Density) (dp)<br />[cero:cracks](Cracks) (dp)<br />[cero:photo](Photo) (dp)<br />[cero:accessibility](Accessibility) (dp)<br />[cero:compressiveStrength](Compressivestrength) (dp)<br />[cero:remainingServiceLife](Remainingservicelife) (dp)<br />[cero:diameter](Diameter) (dp)<br />[cero:loadBearingCapacity](loadbearingcapacity) (dp)<br />[cero:materialResources](Materialresources) (dp)<br />[cero:reinforcingSteelTensileStrength](Reinforcingsteeltensilestrength) (dp)<br />[cero:length](Length) (dp)<br />[cero:location](Location) (dp)<br />[cero:concreteCover](Concretecover) (dp)<br />[cero:youngModulus](Youngmodulus) (dp)<br />[cero:dceClassification](DCEClassification) (dp)<br />[cero:exposureClass](Exposureclass) (dp)<br />[cero:initialFunction](Initialfunction) (dp)<br />[cero:loadHistory](Loadhistory) (dp)<br />[cero:shapeCategory](Shapecategory) (dp)<br />[cero:workingHours](Workinghours) (dp)<br />[cero:width](Width) (dp)<br />[cero:damageClass](Damageclass) (dp)<br />[cero:crossSection](Crosssection) (dp)<br />[cero:reinforcementTensileStrength](Reinforcementtensilestrength) (dp)<br />[cero:color](Color) (dp)<br />[cero:machineResources](Machineresources) (dp)<br />[cero:carbonationDepth](Carbonationdepth) (dp)<br />[cero:reinforcementLayout](Reinforcementlayout) (dp)<br />[cero:reinforcementYoungModulus](Reinforcementyoungmodulus) (dp)<br />[cero:reinforcementMass](Reinforcementmass) (dp)<br />[cero:finishing](Finishing) (dp)<br />[cero:reinforcementRatio](Reinforcementratio) (dp)<br />[cero:height](Height) (dp)<br />[cero:crackWidth](Crackwidth) (dp)<br />[cero:identifier](identifier) (dp)<br />[cero:environmentalActions](environmentalactions) (dp)<br />[cero:internalDefects](Internaldefects) (dp)<br />[cero:environmentalImpact](environmentalimpact) (dp)<br />[cero:toxicSubstances](Toxicsubstances) (dp)<br />
### GroupOfProperties
Property | Value
--- | ---
IRI | `https://w3id.org/isoprops#GroupOfProperties`
### Property
Property | Value
--- | ---
IRI | `https://w3id.org/isoprops#Property`
Sub-classes |[metadata4ing:TextVariable](http://w3id.org/nfdi4ing/metadata4ing#TextVariable) (c)<br />

## Datatype Properties
[Accessibility](#Accessibility),
[Anchor points](#Anchorpoints),
[Carbonation depth](#Carbonationdepth),
[Chloride content](#Chloridecontent),
[Color](#Color),
[Compressive strength](#Compressivestrength),
[Concrete compressive strength](#Concretecompressivestrength),
[Concrete cover](#Concretecover),
[Concrete stiffness](#Concretestiffness),
[Connection type](#Connectiontype),
[Crack width](#Crackwidth),
[Cracks](#Cracks),
[Cross section](#Crosssection),
[Damage class](#Damageclass),
[DCE Classification](#DCEClassification),
[Density](#Density),
[Diameter](#Diameter),
[element dimensions](#elementdimensions),
[element type](#elementtype),
[Energy consumed](#Energyconsumed),
[environmental actions](#environmentalactions),
[environmental impact](#environmentalimpact),
[Exposure class](#Exposureclass),
[Extraordinary damage](#Extraordinarydamage),
[Finishing](#Finishing),
[Height](#Height),
[identifier](#identifier),
[Initial function](#Initialfunction),
[Initial project](#Initialproject),
[Internal defects](#Internaldefects),
[Length](#Length),
[load bearing capacity](#loadbearingcapacity),
[Load history](#Loadhistory),
[Location](#Location),
[Machine resources](#Machineresources),
[Material resources](#Materialresources),
[origin](#origin),
[Photo](#Photo),
[Reinforcement layout](#Reinforcementlayout),
[Reinforcement mass](#Reinforcementmass),
[Reinforcement ratio](#Reinforcementratio),
[Reinforcement tensile strength](#Reinforcementtensilestrength),
[Reinforcement young modulus](#Reinforcementyoungmodulus),
[Reinforcing steel tensile strength](#Reinforcingsteeltensilestrength),
[Remaining service life](#Remainingservicelife),
[Shape category](#Shapecategory),
[Toxic substances](#Toxicsubstances),
[Transport distance](#Transportdistance),
[Volume](#Volume),
[Weight](#Weight),
[Width](#Width),
[Working hours](#Workinghours),
[Young modulus](#Youngmodulus),
[](Accessibility)
### Accessibility
Property | Value
--- | ---
IRI | `https://w3id.org/cero#accessibility`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Anchorpoints)
### Anchor points
Property | Value
--- | ---
IRI | `https://w3id.org/cero#anchorPoints`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Carbonationdepth)
### Carbonation depth
Property | Value
--- | ---
IRI | `https://w3id.org/cero#carbonationDepth`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Chloridecontent)
### Chloride content
Property | Value
--- | ---
IRI | `https://w3id.org/cero#chlorideContent`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Color)
### Color
Property | Value
--- | ---
IRI | `https://w3id.org/cero#color`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Compressivestrength)
### Compressive strength
Property | Value
--- | ---
IRI | `https://w3id.org/cero#compressiveStrength`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Concretecompressivestrength)
### Concrete compressive strength
Property | Value
--- | ---
IRI | `https://w3id.org/cero#concreteCompressiveStrength`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
[](Concretecover)
### Concrete cover
Property | Value
--- | ---
IRI | `https://w3id.org/cero#concreteCover`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Concretestiffness)
### Concrete stiffness
Property | Value
--- | ---
IRI | `https://w3id.org/cero#concreteStiffness`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
[](Connectiontype)
### Connection type
Property | Value
--- | ---
IRI | `https://w3id.org/cero#connectionType`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Crackwidth)
### Crack width
Property | Value
--- | ---
IRI | `https://w3id.org/cero#crackWidth`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Cracks)
### Cracks
Property | Value
--- | ---
IRI | `https://w3id.org/cero#cracks`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Crosssection)
### Cross section
Property | Value
--- | ---
IRI | `https://w3id.org/cero#crossSection`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Damageclass)
### Damage class
Property | Value
--- | ---
IRI | `https://w3id.org/cero#damageClass`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](DCEClassification)
### DCE Classification
Property | Value
--- | ---
IRI | `https://w3id.org/cero#dceClassification`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Density)
### Density
Property | Value
--- | ---
IRI | `https://w3id.org/cero#density`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Diameter)
### Diameter
Property | Value
--- | ---
IRI | `https://w3id.org/cero#diameter`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](elementdimensions)
### element dimensions
Property | Value
--- | ---
IRI | `https://w3id.org/cero#elementDimensions`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](elementtype)
### element type
Property | Value
--- | ---
IRI | `https://w3id.org/cero#elementType`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Energyconsumed)
### Energy consumed
Property | Value
--- | ---
IRI | `https://w3id.org/cero#energyConsumed`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](environmentalactions)
### environmental actions
Property | Value
--- | ---
IRI | `https://w3id.org/cero#environmentalActions`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](environmentalimpact)
### environmental impact
Property | Value
--- | ---
IRI | `https://w3id.org/cero#environmentalImpact`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Exposureclass)
### Exposure class
Property | Value
--- | ---
IRI | `https://w3id.org/cero#exposureClass`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Extraordinarydamage)
### Extraordinary damage
Property | Value
--- | ---
IRI | `https://w3id.org/cero#extraordinaryDamage`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Finishing)
### Finishing
Property | Value
--- | ---
IRI | `https://w3id.org/cero#finishing`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Height)
### Height
Property | Value
--- | ---
IRI | `https://w3id.org/cero#height`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](identifier)
### identifier
Property | Value
--- | ---
IRI | `https://w3id.org/cero#identifier`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Initialfunction)
### Initial function
Property | Value
--- | ---
IRI | `https://w3id.org/cero#initialFunction`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Initialproject)
### Initial project
Property | Value
--- | ---
IRI | `https://w3id.org/cero#initialProject`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Internaldefects)
### Internal defects
Property | Value
--- | ---
IRI | `https://w3id.org/cero#internalDefects`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Length)
### Length
Property | Value
--- | ---
IRI | `https://w3id.org/cero#length`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](loadbearingcapacity)
### load bearing capacity
Property | Value
--- | ---
IRI | `https://w3id.org/cero#loadBearingCapacity`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Loadhistory)
### Load history
Property | Value
--- | ---
IRI | `https://w3id.org/cero#loadHistory`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Location)
### Location
Property | Value
--- | ---
IRI | `https://w3id.org/cero#location`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Machineresources)
### Machine resources
Property | Value
--- | ---
IRI | `https://w3id.org/cero#machineResources`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Materialresources)
### Material resources
Property | Value
--- | ---
IRI | `https://w3id.org/cero#materialResources`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](origin)
### origin
Property | Value
--- | ---
IRI | `https://w3id.org/cero#origin`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Photo)
### Photo
Property | Value
--- | ---
IRI | `https://w3id.org/cero#photo`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
[](Reinforcementlayout)
### Reinforcement layout
Property | Value
--- | ---
IRI | `https://w3id.org/cero#reinforcementLayout`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Reinforcementmass)
### Reinforcement mass
Property | Value
--- | ---
IRI | `https://w3id.org/cero#reinforcementMass`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Reinforcementratio)
### Reinforcement ratio
Property | Value
--- | ---
IRI | `https://w3id.org/cero#reinforcementRatio`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Reinforcementtensilestrength)
### Reinforcement tensile strength
Property | Value
--- | ---
IRI | `https://w3id.org/cero#reinforcementTensileStrength`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Reinforcementyoungmodulus)
### Reinforcement young modulus
Property | Value
--- | ---
IRI | `https://w3id.org/cero#reinforcementYoungModulus`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Reinforcingsteeltensilestrength)
### Reinforcing steel tensile strength
Property | Value
--- | ---
IRI | `https://w3id.org/cero#reinforcingSteelTensileStrength`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Remainingservicelife)
### Remaining service life
Property | Value
--- | ---
IRI | `https://w3id.org/cero#remainingServiceLife`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:integer](http://www.w3.org/2001/XMLSchema#integer) (c)<br />
[](Shapecategory)
### Shape category
Property | Value
--- | ---
IRI | `https://w3id.org/cero#shapeCategory`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Toxicsubstances)
### Toxic substances
Property | Value
--- | ---
IRI | `https://w3id.org/cero#toxicSubstances`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Transportdistance)
### Transport distance
Property | Value
--- | ---
IRI | `https://w3id.org/cero#transportDistance`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Volume)
### Volume
Property | Value
--- | ---
IRI | `https://w3id.org/cero#volume`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Weight)
### Weight
Property | Value
--- | ---
IRI | `https://w3id.org/cero#weight`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Width)
### Width
Property | Value
--- | ---
IRI | `https://w3id.org/cero#width`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />
[](Workinghours)
### Working hours
Property | Value
--- | ---
IRI | `https://w3id.org/cero#workingHours`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:string](http://www.w3.org/2001/XMLSchema#string) (c)<br />
[](Youngmodulus)
### Young modulus
Property | Value
--- | ---
IRI | `https://w3id.org/cero#youngModulus`
Domain(s) |[bot:Element](https://w3id.org/bot#Element) (c)<br />
Range(s) |[xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal) (c)<br />

## Named Individuals
[Condition & Assessment](#ConditionAssessment),
[Factsheet](#Factsheet),
[Geometric](#Geometric),
[Identification](#Identification),
[Inspection certificate properties](#Inspectioncertificateproperties),
[Inspection form](#Inspectionform),
[Organization CRC1883](#OrganizationCRC1883),
[Physical & Material](#PhysicalMaterial),
[Process & Lifecycle](#ProcessLifecycle),
[Properties related to the inspection report](#Propertiesrelatedtotheinspectionreport),
[Properties related to the sustainability assessment ](#Propertiesrelatedtothesustainabilityassessment),
[Reuse properties of CRC1683](#ReusepropertiesofCRC1683),
[Section 1: General Element and Project Information](#Section1:GeneralElementandProjectInformation),
[Section 2.1: Mechanical Properties](#Section2.1:MechanicalProperties),
[Section 2.2: Geometry and damage](#Section2.2:Geometryanddamage),
[Section 2: Condition Assessment](#Section2:ConditionAssessment),
[Section 3: Durability and Remaining Service Life](#Section3:DurabilityandRemainingServiceLife),
[Sustainability assessment properties](#Sustainabilityassessmentproperties),
### Section 1: General Element and Project Information <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_1_GeneralInformation`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Identification <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_1_Identification`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Section 2.1: Mechanical Properties <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_2_1_MechanicalProperties`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Section 2.2: Geometry and damage <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_2_2_GeometryDamage`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Section 2: Condition Assessment <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_2_ConditionAssessment`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Geometric <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_2_Geometric`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Section 3: Durability and Remaining Service Life <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_3_Durability`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Physical & Material <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_3_PhysicalAndMaterial`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Condition & Assessment <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_4_ConditionAndAssessment`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Process & Lifecycle <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Group_5_ProcessAndLifecycle`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Inspection certificate properties <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#InspectionCertificateProperties`
* **Contributor(s)**
  * [isoprops:DictionarySubset](https://w3id.org/isoprops#DictionarySubset)
### Properties related to the inspection report <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#InspectionReport`
* **Contributor(s)**
  * [isoprops:DictionaryReferenceDocument](https://w3id.org/isoprops#DictionaryReferenceDocument)
### Organization CRC1883 <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Organization_CRC1883`
* **Contributor(s)**
  * [prov:Organization](http://www.w3.org/ns/prov#Organization)
### Inspection form <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Ref_1_Form`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Factsheet <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#Ref_2_FactSheet`
* **Contributor(s)**
  * [isoprops:GroupOfProperties](https://w3id.org/isoprops#GroupOfProperties)
### Reuse properties of CRC1683 <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#ReuseProperties`
* **Contributor(s)**
  * [isoprops:Dictionary](https://w3id.org/isoprops#Dictionary)
### Sustainability assessment properties <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#SustainabilityAssessmentProperties`
* **Contributor(s)**
  * [isoprops:DictionarySubset](https://w3id.org/isoprops#DictionarySubset)
### Properties related to the sustainability assessment  <sup>c</sup>
Property | Value
--- | ---
IRI | `https://w3id.org/cero#SustainabilityAssessmentReport`
* **Contributor(s)**
  * [isoprops:DictionaryReferenceDocument](https://w3id.org/isoprops#DictionaryReferenceDocument)
## Namespaces
* **default (:)**
  * `https://w3id.org/cero#`
* **bot**
  * `https://w3id.org/bot#`
* **cero**
  * `https://w3id.org/cero#`
* **dc**
  * `http://purl.org/dc/terms/`
* **dcat**
  * `http://www.w3.org/ns/dcat#`
* **isoprops**
  * `https://w3id.org/isoprops#`
* **metadata4ing**
  * `http://w3id.org/nfdi4ing/metadata4ing#`
* **owl**
  * `http://www.w3.org/2002/07/owl#`
* **prov**
  * `http://www.w3.org/ns/prov#`
* **rdf**
  * `http://www.w3.org/1999/02/22-rdf-syntax-ns#`
* **rdfs**
  * `http://www.w3.org/2000/01/rdf-schema#`
* **sdo**
  * `https://schema.org/`
* **sh**
  * `http://www.w3.org/ns/shacl#`
* **skos**
  * `http://www.w3.org/2004/02/skos/core#`
* **tempo**
  * `https://w3id.org/tempo#`
* **unit**
  * `http://qudt.org/vocab/unit#`
* **vann**
  * `http://purl.org/vocab/vann/`
* **voaf**
  * `http://purl.org/vocommons/voaf#`
* **xml**
  * `http://www.w3.org/XML/1998/namespace`
* **xsd**
  * `http://www.w3.org/2001/XMLSchema#`

## Legend
* Classes: c
* Object Properties: op
* Functional Properties: fp
* Data Properties: dp
* Annotation Properties: dp
* Properties: p
* Named Individuals: ni
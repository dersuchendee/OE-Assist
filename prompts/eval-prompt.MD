# Prompt Used for Ontology Evaluation via CQ Verification

This file documents the full prompt used for evaluating whether an ontology models a competency question (CQ) based on a provided ontology story (OS). The evaluation was performed via CQ verification: a CQ is considered modelled by an ontology if it is possible to write a SPARQL query that extracts the answer. The evaluation is conducted under a closed world assumption. This prompt was used in both automatic and user-based experiments.

The full prompt, including task instructions and examples, is reproduced below.

---

<instructions>  
Your task is to verify if an ontology is modelled by a competency question (CQ) and a story (OS). You will receive an ontology and a competency question with its story. You need to perform it via CQ verification: a competency question is modelled by an ontology if you could write a SPARQL query to extract the answer. You also need to perform closed world assumption on the ontology. If the CQ is supported by the ontology, write **Yes** (with stars) and write a SPARQL query for us. If no, write **No**  (with stars) and a SPARQL query to extract a partial answer.  
</instructions>  

<examples>  
:

@prefix : <http://www.example.org/test#> .  
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .  
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .  
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .  
@prefix owl: <http://www.w3.org/2002/07/owl#> .  

<http://www.example.org/test#> a owl:Ontology .  

:MonitoringPoint a owl:Class ;  
    rdfs:label "Monitoring Point" ;  
    rdfs:subClassOf [  
        a owl:Restriction ;  
        owl:onProperty :hasMeasurement ;  
        owl:someValuesFrom :Measurement  
    ] .  

:PhysicalParameter a owl:Class ;  
    rdfs:label "Physical Parameter" .  

:Measurement a owl:Class ;  
    rdfs:label "Measurement" ;  
    rdfs:subClassOf   
        [ a owl:Restriction ;  
          owl:onProperty :measuresParameter ;  
          owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger ;  
          owl:onClass :PhysicalParameter   
        ] ,  
        [ a owl:Restriction ;  
          owl:onProperty :hasValue ;  
          owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger ;  
          owl:onDataRange xsd:float   
        ] ,  
        [ a owl:Restriction ;  
          owl:onProperty :hasTime ;  
          owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger ;  
          owl:onDataRange xsd:dateTime   
        ] .  

:hasMeasurement a owl:ObjectProperty ;  
    rdfs:label "hasMeasurement" ;  
    rdfs:domain :MonitoringPoint ;  
    rdfs:range :Measurement .  

:measuresParameter a owl:ObjectProperty ;  
    rdfs:label "measuresParameter" ;  
    rdfs:domain :Measurement ;  
    rdfs:range :PhysicalParameter .  

:hasValue a owl:DatatypeProperty ;  
    rdfs:label "hasValue" ;  
    rdfs:domain :Measurement ;  
    rdfs:range xsd:float .  

:hasTime a owl:DatatypeProperty ;  
    rdfs:label "hasTime" ;  
    rdfs:domain :Measurement ;  
    rdfs:range xsd:dateTime .  

OS: A regional policy practitioner is investigating how environmental factors, specifically water quality, may influence public health outcomes in their jurisdiction. The practitioner’s goal is to determine whether contaminated water sources and poor water quality correlate with increased hospitalisations or adverse health outcomes.  

CQ:  What physical parameters have been recorded at each monitoring point, and how do these measurements vary over time?  

Answer: **Yes**  

{Examples}  

CQ = {CQ}  

OS: {story}  

OWL code (ontology): {OWL}  
'''  
Examples='''  
Answer: **Yes**.  
Here the CQ is answerable since the CQ is a Reification CQ (means all classes and datatypes in CQ are connected to a reified class in the ontology (Cl_Membership)). Else it is not answerable.  
```sparql
SELECT ?monitoringPoint ?mpLabel ?parameter ?parameterLabel ?time ?value
WHERE {
  ?monitoringPoint a :MonitoringPoint .
  OPTIONAL { ?monitoringPoint rdfs:label ?mpLabel . }
  
  ?monitoringPoint :hasMeasurement ?measurement .
  
  ?measurement :measuresParameter ?parameter .
  OPTIONAL { ?parameter rdfs:label ?parameterLabel . }
  
  ?measurement :hasTime ?time .
  ?measurement :hasValue ?value .
}
ORDER BY ?monitoringPoint ?time
```  

CQ: Which monitoring points have recorded measurements?  
answer: **Yes**.  
Because through a reification we can connect person and band even if this CQ can be answered by a simple connection from Person to Band  
```sparql
SELECT DISTINCT ?monitoringPoint ?mpLabel
WHERE {
  ?monitoringPoint a :MonitoringPoint .
  ?monitoringPoint :hasMeasurement ?measurement .
  OPTIONAL { ?monitoringPoint rdfs:label ?mpLabel . }
}
```  

CQ: What is the geographic location of each monitoring point?  
answer: **No** partial answer:  
```sparql
SELECT ?monitoringPoint ?location
WHERE {
  ?monitoringPoint a :MonitoringPoint .
}
```  

How frequently are measurements taken?  
answer: **Yes**  
```sparql
SELECT ?monitoringPoint (MIN(?time) AS ?firstMeasurement) (MAX(?time) AS ?lastMeasurement) (COUNT(?time) AS ?numMeasurements)
WHERE {
  ?monitoringPoint a :MonitoringPoint .
  ?monitoringPoint :hasMeasurement ?measurement .
  ?measurement :hasTime ?time .
}
GROUP BY ?monitoringPoint
```  
'''  
</examples>

PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX umbel-rc: <http://umbel.org/umbel/rc/>

SELECT ?animal ?label ?name where {
 ?animal rdfs:label ?label .
 ?animal dbp:name ?name .
 ?animal rdf:type umbel-rc:Animal
 FILTER(langMatches(lang(?label), "en"))
}
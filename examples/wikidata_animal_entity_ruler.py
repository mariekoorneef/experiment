"""Example of a spaCy v2.1 EntityRuler that uses extracted patterns
from wikidata using SPARQLWrapper

* spaCy EntityRuler: https://spacy.io/usage/rule-based-matching#entityruler
* SPARQL: https://github.com/RDFLib/sparqlwrapper

"""

import spacy
from spacy.pipeline import EntityRuler
from jinja2 import Template
from pkg_resources import resource_filename
from SPARQLWrapper import SPARQLWrapper, JSON
import plac


@plac.annotations(
    text=("Text to process", "positional", None, str)
)
def main(text="The american bison has been eaten by the crocodile"):
    nlp = spacy.load("en_core_web_sm")
    # Initialize the entity ruler
    ruler = EntityRuler(nlp, overwrite_ents=True)
    assert len(ruler) == 0

    # get animal patters
    patterns = get_animal_pattern()

    # add petterns
    ruler.add_patterns(patterns)
    assert len(ruler) == len(patterns)
    nlp.add_pipe(ruler)

    doc = nlp(text)
    print("Wikidata has {} english Animal pages".format(len(patterns)))  # size of animal list
    print("Tokens", [t.text for t in doc])  # animals are not merged
    print("Entities", [(ent.text, ent.label_) for ent in doc.ents]) # all animals are entities


def get_animal_pattern():
    # open sparql file to extract query
    with open(resource_filename(__name__, 'sparql/animal.sql')) as f:
        QUERY = f.read()

    query = Template(QUERY).render()

    # Initialize the SPARQLWrapper
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    patterns = [{"label": "ANIMAL", "pattern": [{"LOWER": r.lower()}
                                                for r in result["label"]["value"].split()]}
                for result in results["results"]["bindings"]]

    return patterns


if __name__ == "__main__":
    plac.call(main)

    # Expected output:
    # Wikidata has 861 english Animal pages
    # Tokens ['The', 'american', 'bison', 'has', 'been', 'eaten', 'by', 'the', 'crocodile']
    # Entities [('american bison', 'ANIMAL'), ('crocodile', 'ANIMAL')]

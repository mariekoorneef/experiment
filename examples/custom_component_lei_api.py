"""Example of a spaCy v2.1 pipeline component that requests Legal Entity Identifier (LEI)
from the REST LEILex API, merges LEI names into one token and assigns entity
labels

* REST LEILex API: https://www.leilex.com/api/
* REST gleif LEI Search 2.0 API: https://leilookup.gleif.org/docs/v2
* Adjusted https://github.com/explosion/spaCy/tree/master/examples/pipeline to
    What's New in v2.1: https://spacy.io/usage/v2-1

"""

import requests
import plac
import spacy
from spacy.tokens import Doc, Span, Token
from spacy.pipeline import EntityRuler


@plac.annotations(
    text=("Text to process", "positional", None, str)
)
def main(text=None):
    # Use the spaCy model
    nlp = spacy.load("en_core_web_sm")
    # get lei
    lei = get_leilex_list()
    if not text:  # set default text if none is set
        text = "The company {} is located in the Netherlands".format([c['LegalName']
                                                                      for c in lei['records']][10])

    rest_lei = RESTLEIComponent(nlp=nlp, lei=lei)  # initialise component
    nlp.add_pipe(rest_lei)  # add it to the pipeline
    doc = nlp(text)
    print("Pipeline", nlp.pipe_names)  # pipeline contains component name
    print("Doc has LEI companies", doc._.has_lei)  # Doc contains leis
    print("Token", [t.text for t in doc])  # LEI are merged
    print("Entities", [(e.text, e.label_) for e in doc.ents])  # entities


def get_leilex_list():
    """returns a list of 50 LEI"""
    url = 'https://api.leilex.com/API/LEI/'
    payload = {
        'country': 'NL',
        'RegistrationStatus': 'ISSUED'
    }

    r = requests.get(url, params=payload)
    r.raise_for_status()  # raise an error if request fails
    return r.json()


class RESTLEIComponent(object):
    """spaCy v2.1 pipeline component that requests 50 LEI companies
    the REST LEILex API, merges company names into one token, assigns entity
    labels and sets attributes on company tokens.
    """

    name = "rest_lei"  # component name, will show up in the pipeline

    def __init__(self, nlp, lei, label="LEI"):
        """Initialise the pipeline component. The shared nlp instance is used
        to initialise the ruler with the shared vocab, generate Doc objects as
        phrase match patterns.
        """
        # Make request once on initialisation and store the data
        self.label = label

        # Set up the EntityRuler
        patterns = [{"label": self.label, "pattern": [{"LOWER": r.lower()}
                                                    for r in result["LegalName"].split()]}
                    for result in lei["records"]]
        self.ruler = EntityRuler(nlp, overwrite_ents=True)
        self.ruler.add_patterns(patterns=patterns)

        # Register attribute on the Token with default value.
        # I will overwrite this based on the matches.
        Token.set_extension("is_lei", default=False)

        # Register attributes on Doc and Span via a getter that checks if one of
        # the contained tokens is set to is_lei == True.
        Doc.set_extension("has_lei", getter=self.has_lei)
        Span.set_extension("has_lei", getter=self.has_lei)

    def __call__(self, doc):
        """Apply the pipeline component on a Doc object and modify it if matches
        are found. Return the Doc, so it can be processed by the next component
        in the pipeline, if available.
        """
        ruler = self.ruler(doc)  # execute the ruler

        spans = []  # keep the spans for later so we can merge them afterwards
        for _,start, end in self.ruler.matcher(doc):
            # Generate Span representing the entity & set label
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            # Set custom attribute on each token of the entity
            # Can be extended with other data returned by the API, like
            # lei_code, country
            for token in entity:
                token._.set("is_lei", True)

        with doc.retokenize() as retokenizer:
            # Iterate over all spans en merge spans of multiple tokens into one single token
            for span in spans:
                retokenizer.merge(span)

        return doc

    def has_lei(self, tokens):
        """Getter for Doc and Span attributes. Returns True if one of the tokens
        is a LEI company."""
        return any([t._.get("is_lei") for t in tokens])


if __name__ == "__main__":
    plac.call(main)

    # Expected output
    # Pipeline ['tagger', 'parser', 'ner', 'rest_leilex']
    # Doc has LEI companies True
    # Token ['The', 'company', '@vanVeen B.V.', 'is', 'located', 'in', 'the', 'Netherlands']
    # Entities [('@vanVeen B.V.', 'LEI'), ('Netherlands', 'GPE')]

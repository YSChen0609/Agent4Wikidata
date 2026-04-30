"""Very simple Wikidata SPARQL example using SPARQLWrapper.

Run (from this directory):
    uv run python wikidata_call.py
"""

from SPARQLWrapper import JSON, SPARQLWrapper

from ask_wikidata import __version__

ENDPOINT = "https://query.wikidata.org/sparql"

USER_AGENT = f"ask-wikidata/{__version__} (Wikidata SPARQL client; local/dev)"


def wikidata_query_call(query: str) -> dict:
    """Execute a SPARQL query against the Wikidata endpoint."""

    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setReturnFormat(JSON)
    sparql.addCustomHttpHeader("User-Agent", USER_AGENT)
    sparql.setQuery(query)
    return sparql.query().convert()


if __name__ == "__main__":
    sample_query = """
    SELECT ?item ?itemLabel WHERE {
      ?item wdt:P31 wd:Q146 .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    LIMIT 1
    """
    data = wikidata_query_call(sample_query)
    print(data)
    rows = data["results"]["bindings"]
    if not rows:
        print("No rows returned.")
    else:
        row = rows[0]
        print("item:", row["item"]["value"])
        print("itemLabel:", row["itemLabel"]["value"])


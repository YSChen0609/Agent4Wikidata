import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from langchain_core.tools import tool

from ask_wikidata import __version__

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
DEFAULT_USER_AGENT = (
    f"ask-wikidata/{__version__} (Wikidata lookup tool; local/dev)"
)


def _search_wikidata_id(
    search_text: str,
    *,
    entity_type: str,
    id_prefix: str,
    language: str = "en",
) -> str | None:
    """Generic Wikidata ID search helper for items/properties."""

    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": language,
        "type": entity_type,
        "search": search_text,
        "limit": 1,
    }
    url = f"{WIKIDATA_API}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    results = payload.get("search", [])
    if not results:
        return None

    found_id = results[0].get("id")
    if isinstance(found_id, str) and found_id.startswith(id_prefix):
        return found_id
    return None


def search_entity_qid(entity_text: str, language: str = "en") -> str | None:
    """Return the top Wikidata QID match for a given entity text."""

    return _search_wikidata_id(
        entity_text,
        entity_type="item",
        id_prefix="Q",
        language=language,
    )


def search_property_pid(property_text: str, language: str = "en") -> str | None:
    """Return the top Wikidata PID match for a given property text."""

    return _search_wikidata_id(
        property_text,
        entity_type="property",
        id_prefix="P",
        language=language,
    )


@tool
def search_entity_qid_tool(entity_text: str, language: str = "en") -> str:
    """Search Wikidata and return top entity QID (e.g. France -> Q142)."""

    qid = search_entity_qid(entity_text=entity_text, language=language)
    return qid or "NOT_FOUND"


@tool
def search_property_pid_tool(property_text: str, language: str = "en") -> str:
    """Search Wikidata and return top property PID (e.g. capital -> P36)."""

    pid = search_property_pid(property_text=property_text, language=language)
    return pid or "NOT_FOUND"


WIKIDATA_LOOKUP_TOOLS = [
    search_entity_qid_tool,
    search_property_pid_tool,
]


if __name__ == "__main__":
    entity = "France"
    qid = search_entity_qid(entity)
    print(f'Entity: "{entity}"')
    print(f"QID: {qid or 'Not found'}")

    prop = "capital"
    pid = search_property_pid(prop)
    print(f'Property: "{prop}"')
    print(f"PID: {pid or 'Not found'}")


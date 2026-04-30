"""Prompt templates for NL -> Wikidata SPARQL generation."""

from langchain_core.prompts import ChatPromptTemplate

WIKIDATA_SPARQL_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a Wikidata SPARQL generator with tool access.\n"
            "You are exposed to these tools:\n"
            "- search_entity_qid_tool(entity_text, language='en') -> QID|NOT_FOUND\n"
            "- search_property_pid_tool(property_text, language='en') -> PID|NOT_FOUND\n\n"
            "Goal: Convert the user question into one valid Wikidata SPARQL SELECT query.\n\n"
            "Mandatory process:\n"
            "1) Call tools to resolve IDs before writing the query.\n"
            "   - Use `search_entity_qid_tool` to resolve entities to QIDs.\n"
            "   - Use `search_property_pid_tool` to resolve properties to PIDs.\n"
            "2) Build triple patterns in this shape: `wd:QID wdt:PID ?object`.\n"
            "3) Return only the raw SPARQL query.\n\n"
            "General instructions:\n"
            "- Final output must start with `SELECT` and contain ONLY the SPARQL query text.\n"
            "- No markdown fences, no comments, no explanations.\n"
            "- Do not invent QIDs/PIDs.\n"
            "- Use `SERVICE wikibase:label {{ bd:serviceParam wikibase:language "
            "\"[AUTO_LANGUAGE],en\". }}` when returning labels.\n"
            "- Prefer `wdt:` direct properties for simple factual lookups.\n"
            "- If you cannot resolve a required QID/PID, return exactly: NEED_DISAMBIGUATION\n\n"
            "Examples:\n"
            "Question: What is the capital of France?\n"
            "SPARQL:\n"
            "SELECT ?capital ?capitalLabel WHERE {{\n"
            "  wd:Q142 wdt:P36 ?capital .\n"
            "  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "
            "\"[AUTO_LANGUAGE],en\". }}\n"
            "}}\n"
            "LIMIT 10\n\n"
            "Question: What is the population of Japan?\n"
            "SPARQL:\n"
            "SELECT ?population WHERE {{\n"
            "  wd:Q17 wdt:P1082 ?population .\n"
            "}}\n"
            "ORDER BY DESC(?population)\n"
            "LIMIT 1\n\n"
            "Question: What is the official website of OpenAI?\n"
            "SPARQL:\n"
            "SELECT ?website WHERE {{\n"
            "  wd:Q24283660 wdt:P856 ?website .\n"
            "}}\n"
            "LIMIT 10"
        ),
        ("human", "Question: {question}"),
    ]
)


def build_wikidata_sparql_prompt(question: str):
    """Return a formatted chat prompt value for SPARQL generation."""
    return WIKIDATA_SPARQL_PROMPT_TEMPLATE.invoke({"question": question})


import os
from typing import Any, NotRequired, Required, TypedDict, cast

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ask_wikidata.llm_backend import build_llm
from ask_wikidata.prompt import WIKIDATA_SPARQL_PROMPT_TEMPLATE
from ask_wikidata.wikidata_call import wikidata_query_call
from ask_wikidata.wikidata_lookup_tools import WIKIDATA_LOOKUP_TOOLS


class QueryGenState(TypedDict, total=False):
    query_nl: Required[str]
    messages: NotRequired[list[BaseMessage]]
    query_sparql: NotRequired[str]
    query_results: NotRequired[dict[str, Any]]


def _extract_first_sparql_select(content: str) -> str:
    """Extract the first `SELECT ...` substring.

    Models sometimes include tool-call JSON/text before the final query.
    Wikidata will fail if we send that extra prefix, so we slice from `SELECT`.
    """

    text = content.strip().strip("`")
    idx = text.find("SELECT")
    if idx == -1:
        return ""
    return text[idx:].strip()


def _initialize_messages(state: QueryGenState) -> QueryGenState:
    """Seed the conversation with the system prompt and user question."""

    query_nl = state["query_nl"].strip()
    prompt_messages = WIKIDATA_SPARQL_PROMPT_TEMPLATE.invoke(
        {"question": query_nl}
    ).to_messages()
    state["messages"] = prompt_messages
    return state


def agent_step(state: QueryGenState, llm: BaseChatModel) -> QueryGenState:
    """Run one model step; may return tool calls or final SPARQL text."""

    messages = state.get("messages", [])
    response = llm.invoke(messages)
    state["messages"] = [*messages, cast(BaseMessage, response)]

    # If the model is done (no tool calls), extract the raw SPARQL from the model output.
    # Do this here (not in the router) so the value reliably persists in state.
    if isinstance(response, AIMessage) and not response.tool_calls:
        content = response.content if isinstance(response.content, str) else str(
            response.content
        )
        state["query_sparql"] = _extract_first_sparql_select(content)
    return state


def execute_query(state: QueryGenState) -> QueryGenState:
    """Execute a SPARQL query and store the results in state."""

    sparql = state.get("query_sparql", "").strip()
    if not sparql:
        state["query_results"] = {"error": "MISSING_QUERY_SPARQL"}
        return state
    state["query_results"] = wikidata_query_call(sparql)
    return state


def build_graph(llm: BaseChatModel):
    """Build and compile ReAct-style NL -> tools -> SPARQL -> execute graph."""

    builder = StateGraph(QueryGenState)
    tool_node = ToolNode(WIKIDATA_LOOKUP_TOOLS)

    builder.add_node("initialize_messages", _initialize_messages)
    builder.add_node("agent_step", lambda state: agent_step(state, llm=llm))
    builder.add_node("tools", tool_node)
    builder.add_node("execute_query", execute_query)

    builder.add_edge(START, "initialize_messages")
    builder.add_edge("initialize_messages", "agent_step")
    builder.add_conditional_edges(
        "agent_step",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "execute_query",
        },
    )
    builder.add_edge("tools", "agent_step")
    builder.add_edge("execute_query", END)
    return builder.compile()


def run_nl_query(
    query_nl: str,
    provider: str | None = os.getenv("LLM_PROVIDER", "ollama"),
    model: str | None = os.getenv("LLM_MODEL"),
) -> QueryGenState:
    """Run the full NL -> SPARQL -> execute pipeline."""

    llm = build_llm(provider=provider, model=model)
    llm_with_tools = llm.bind_tools(WIKIDATA_LOOKUP_TOOLS)
    graph = build_graph(llm_with_tools)
    return cast(QueryGenState, graph.invoke({"query_nl": query_nl}))


if __name__ == "__main__":
    response = run_nl_query("What is the capital of France?")
    print(response.get("query_results", {}))
    print(response.get("query_sparql", ""))


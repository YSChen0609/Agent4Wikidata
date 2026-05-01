"""
Breaking query list for ASK-WIKIDATA stress testing.

Categories:
  AMBIGUOUS   – underspecified questions where the entity/property is unclear
  CONFLICTING – logically contradictory or mutually exclusive constraints
  TYPO        – misspelled entity / property names
  NON_ENGLISH – questions written in languages other than English
"""

from typing import NamedTuple


class BreakingQuery(NamedTuple):
    category: str
    query: str
    note: str


BREAKING_QUERIES: list[BreakingQuery] = [
    # ── AMBIGUOUS ──────────────────────────────────────────────────────────────
    BreakingQuery(
        category="AMBIGUOUS",
        query="Who is the president?",
        note="No country or time frame specified.",
    ),
    BreakingQuery(
        category="AMBIGUOUS",
        query="What is the capital?",
        note="No country specified at all.",
    ),
    BreakingQuery(
        category="AMBIGUOUS",
        query="When did he die?",
        note="Pronoun without any prior context.",
    ),
    BreakingQuery(
        category="AMBIGUOUS",
        query="What is the population of the city?",
        note="No city identified.",
    ),
    BreakingQuery(
        category="AMBIGUOUS",
        query="Who wrote the book?",
        note="No title or author context.",
    ),
    BreakingQuery(
        category="AMBIGUOUS",
        query="What is the area of the country?",
        note="'the country' is unresolvable without context.",
    ),
    BreakingQuery(
        category="AMBIGUOUS",
        query="List all rivers.",
        note="Unbounded query – could return millions of results.",
    ),
    BreakingQuery(
        category="AMBIGUOUS",
        query="What is Mercury?",
        note="Mercury can refer to the planet, the element, or the Roman god.",
    ),

    # ── CONFLICTING ────────────────────────────────────────────────────────────
    BreakingQuery(
        category="CONFLICTING",
        query="Who is the oldest living person born after 2010?",
        note="'Oldest living' + 'born after 2010' is unlikely to be meaningful.",
    ),
    BreakingQuery(
        category="CONFLICTING",
        query="What country is both an island and landlocked?",
        note="Islands cannot be landlocked – mutually exclusive properties.",
    ),
    BreakingQuery(
        category="CONFLICTING",
        query="Find all people who died before they were born.",
        note="Death date < birth date is logically impossible.",
    ),
    BreakingQuery(
        category="CONFLICTING",
        query="Which city has zero population but is still inhabited?",
        note="Contradictory properties: zero population vs. inhabited.",
    ),
    BreakingQuery(
        category="CONFLICTING",
        query="Show me the tallest mountain that is below sea level.",
        note="Tallest mountain cannot simultaneously be below sea level.",
    ),
    BreakingQuery(
        category="CONFLICTING",
        query="What are all languages that are both extinct and currently spoken?",
        note="Extinct and currently-spoken are mutually exclusive.",
    ),

    # ── TYPO ───────────────────────────────────────────────────────────────────
    BreakingQuery(
        category="TYPO",
        query="What is the captial of Frnace?",
        note="'captial' and 'Frnace' are misspelled.",
    ),
    BreakingQuery(
        category="TYPO",
        query="Who founed Micosoft?",
        note="'founed' and 'Micosoft' are misspelled.",
    ),
    BreakingQuery(
        category="TYPO",
        query="Waht is the popullation of Brazel?",
        note="Multiple misspellings throughout.",
    ),
    BreakingQuery(
        category="TYPO",
        query="When was Alber Einsten bron?",
        note="'Alber Einsten' and 'bron' are misspelled.",
    ),
    BreakingQuery(
        category="TYPO",
        query="Whcih counrty won the most Olypmic golds?",
        note="Multiple typos – 'Whcih', 'counrty', 'Olypmic'.",
    ),
    BreakingQuery(
        category="TYPO",
        query="How meny plaents are in the Solr Systm?",
        note="'meny', 'plaents', 'Solr Systm' are all misspelled.",
    ),

    # ── NON_ENGLISH ────────────────────────────────────────────────────────────
    BreakingQuery(
        category="NON_ENGLISH",
        query="Quelle est la capitale de la France?",
        note="French: 'What is the capital of France?'",
    ),
    BreakingQuery(
        category="NON_ENGLISH",
        query="¿Cuál es la población de México?",
        note="Spanish: 'What is the population of Mexico?'",
    ),
    BreakingQuery(
        category="NON_ENGLISH",
        query="Was ist die Hauptstadt von Deutschland?",
        note="German: 'What is the capital of Germany?'",
    ),
    BreakingQuery(
        category="NON_ENGLISH",
        query="日本の首相は誰ですか？",
        note="Japanese: 'Who is the Prime Minister of Japan?'",
    ),
    BreakingQuery(
        category="NON_ENGLISH",
        query="من هو مؤسس شركة أبل؟",
        note="Arabic: 'Who is the founder of Apple Inc.?'",
    ),
    BreakingQuery(
        category="NON_ENGLISH",
        query="Кто написал Войну и мир?",
        note="Russian: 'Who wrote War and Peace?'",
    ),
    BreakingQuery(
        category="NON_ENGLISH",
        query="중국의 수도는 어디입니까?",
        note="Korean: 'What is the capital of China?'",
    ),
]

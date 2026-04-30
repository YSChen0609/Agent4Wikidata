import os
from typing import cast

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


def is_quota_error(exc: Exception) -> bool:
    """Return True when an exception likely indicates API quota exhaustion."""

    message = str(exc).lower()
    return any(
        token in message
        for token in (
            "resource_exhausted",
            "quota exceeded",
            "rate limit",
            "429",
        )
    )


def build_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """Build a chat model using a provider-agnostic interface."""

    provider_name = (provider or os.getenv("LLM_PROVIDER", "gemini")).strip().lower()

    if provider_name == "openai":
        from langchain_openai import ChatOpenAI

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")
        selected_model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        return cast(BaseChatModel, ChatOpenAI(model=selected_model, temperature=temperature))

    if provider_name in {"gemini", "google"}:
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")
        selected_model = model or os.getenv("LLM_MODEL", "gemini-2.0-flash")
        return cast(
            BaseChatModel,
            ChatGoogleGenerativeAI(model=selected_model, temperature=temperature),
        )

    if provider_name == "ollama":
        from langchain_ollama import ChatOllama

        selected_model = model or os.getenv("LLM_MODEL", "llama3.1:8b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return cast(
            BaseChatModel,
            ChatOllama(model=selected_model, temperature=temperature, base_url=base_url),
        )

    raise ValueError(
        f"Unsupported LLM provider '{provider_name}'. " "Use one of: openai, gemini, ollama."
    )


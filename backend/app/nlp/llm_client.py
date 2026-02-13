"""
Multi-LLM client factory.

Supported providers (set via LLM_PROVIDER env var):
    azure   — Azure OpenAI Service (uses DefaultAzureCredential)
    github  — GitHub Models inference endpoint

Returns an OpenAI-compatible client and the model name to use.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_llm_client() -> tuple[Any, str]:
    """
    Factory that selects the correct LLM client and model based on config.

    Supported providers: 'azure', 'github'
    """
    from app.config import settings

    provider = (settings.LLM_PROVIDER or "").lower()

    if provider == "azure":
        return _build_azure_client(settings)

    if provider == "github":
        return _build_github_client(settings)

    raise RuntimeError(
        f"Unsupported or unset LLM_PROVIDER: {settings.LLM_PROVIDER!r}. "
        "Supported providers: 'azure', 'github'. To run rule-based only, leave LLM_PROVIDER empty."
    )


# def _build_azure_client(settings: Any) -> tuple[Any, str]:
#     import openai  # type: ignore

#     if not settings.AZURE_OPENAI_ENDPOINT:
#         raise RuntimeError("AZURE_OPENAI_ENDPOINT is not set")

#     if not settings.AZURE_OPENAI_API_KEY:
#         raise RuntimeError("AZURE_OPENAI_API_KEY is not set")


#     try:
#         from azure.identity import DefaultAzureCredential, get_bearer_token_provider  # type: ignore

#         credential = DefaultAzureCredential()
#         token_provider = get_bearer_token_provider(
#             credential, "https://cognitiveservices.azure.com/.default"
#         )
#         client = openai.AzureOpenAI(
#             azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
#             azure_ad_token_provider=token_provider,
#             api_version=settings.AZURE_OPENAI_API_VERSION,
#             timeout=settings.LLM_TIMEOUT,
#         )
#     except ImportError:
#         # Fallback: use API key auth if azure-identity is not available
#         logger.warning(
#             "azure-identity not installed; falling back to AZURE_OPENAI_API_KEY for Azure"
#         )
#         client = openai.AzureOpenAI(
#             azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
#             api_key=settings.AZURE_OPENAI_API_KEY or "",
#             api_version=settings.AZURE_OPENAI_API_VERSION,
#             timeout=settings.LLM_TIMEOUT,
#         )

#     logger.info("LLM client: Azure OpenAI, deployment=%s", settings.AZURE_OPENAI_DEPLOYMENT)
#     return client, settings.AZURE_OPENAI_DEPLOYMENT

def _build_azure_client(settings: Any) -> tuple[Any, str]:
    """
    Simple Azure OpenAI client (no api_version needed).
    Uses only AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY.
    """
    from openai import OpenAI  # modern OpenAI SDK

    if not settings.AZURE_OPENAI_ENDPOINT:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT is not set")

    if not settings.AZURE_OPENAI_API_KEY:
        raise RuntimeError("AZURE_OPENAI_API_KEY is not set")

    # Create OpenAI client pointing to Azure OpenAI endpoint
    client = OpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        base_url=settings.AZURE_OPENAI_ENDPOINT,
    )

    logger.info("LLM client: Azure OpenAI, deployment=%s", settings.AZURE_OPENAI_DEPLOYMENT)
    return client, settings.AZURE_OPENAI_DEPLOYMENT


def _build_github_client(settings: Any) -> tuple[Any, str]:
    import openai  # type: ignore

    if not settings.GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not set")

    client = openai.OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=settings.GITHUB_TOKEN,
        timeout=settings.LLM_TIMEOUT,
    )
    logger.info("LLM client: GitHub Models, model=%s", settings.GITHUB_MODEL)
    return client, settings.GITHUB_MODEL

import os


class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    CORRELATION_ID_HEADER: str = "X-Correlation-ID"

    # ---------------------------------------------------------------------------
    # LLM provider selection
    # Supported: "azure", "github"
    # Default: none (empty) → rule-based NLP only
    # ---------------------------------------------------------------------------
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")  # default empty = no LLM
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "10"))

    # -- Azure OpenAI ----------------------------------------------------------
    AZURE_OPENAI_ENDPOINT: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_API_KEY: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    # AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

    # -- GitHub Models ---------------------------------------------------------
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
    GITHUB_MODEL: str = os.getenv("GITHUB_MODEL", "openai/gpt-4o")

    def llm_enabled(self) -> bool:
        """Return True if an enabled LLM provider is configured."""
        p = (self.LLM_PROVIDER or "").lower()
        if p == "azure":
            return bool(self.AZURE_OPENAI_ENDPOINT)
        if p == "github":
            return bool(self.GITHUB_TOKEN)
        return False


settings = Settings()

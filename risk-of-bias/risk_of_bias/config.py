from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for risk-of-bias tool.

    Settings can be provided via environment variables or a .env file.
    Environment variables should be prefixed appropriately (e.g., OPENAI_API_KEY).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model selection
    fast_ai_model: str = "gpt-4o-mini"
    good_ai_model: str = "gpt-4o"
    best_ai_model: str = "gpt-4o"

    # OpenAI API settings
    temperature: float = 0.2
    openai_api_key: Optional[str] = None

    # Azure OpenAI settings
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-08-06"
    azure_openai_deployment_name: Optional[str] = None

    @property
    def use_azure(self) -> bool:
        """Check if Azure OpenAI should be used based on available settings."""
        return bool(self.azure_openai_endpoint and self.azure_openai_api_key)


settings = Settings()

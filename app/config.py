# Import settings tools from Pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


# This class stores the application settings
class Settings(BaseSettings):

    # PostgreSQL connection settings
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # OpenAI API key for AI features
    # It can be empty for now
    openai_api_key: str | None = None

    # Read configuration values from the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Create the settings object
# We can use this object in other files
settings = Settings()
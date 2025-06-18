import os


class Settings:
    def __init__(self):

        from dotenv import load_dotenv

        load_dotenv()
        self._conn_str: str = os.getenv("CONNECTION_STRING")
        self._endpoint: str = os.getenv("ENDPOINT")
        self._version: str = os.getenv("VERSION")
        self._model: str = os.getenv("MODEL", "gpt-4o")
        self._key: str = os.getenv("KEY")
        if not self._version:
            raise ValueError("Version is not set in the environment variables.")
        if not self._endpoint:
            raise ValueError("Endpoint is not set in the environment variables.")
        if not self._conn_str:
            raise ValueError(
                "Connection string is not set in the environment variables."
            )
        if not self._model:
            raise ValueError("Model is not set in the environment variables.")
        if not self._key:
            raise ValueError("Key is not set in the environment variables.")

    @property
    def connection_string(self) -> str:
        """Get the connection string for the Azure AI Project Client."""
        if self._conn_str is None:
            raise ValueError("Connection string is not set.")
        return self._conn_str

    @property
    def endpoint(self) -> str:
        """Get the endpoint for the Azure AI Project Client."""
        if self._endpoint is None:
            raise ValueError("Endpoint is not set.")
        return self._endpoint

    @property
    def version(self) -> str:
        """Get the version of the Azure AI Project Client."""
        return self._version

    @property
    def model(self) -> str:
        """Get the model name for the Azure AI Project Client."""
        if self._model is None:
            raise ValueError("Model is not set.")
        return self._model

    @property
    def key(self) -> str:
        """Get the API key for the Azure AI Project Client."""
        if self._key is None:
            raise ValueError("Key is not set.")
        return self._key


setting_singleton = None


def get_settings() -> Settings:
    global setting_singleton
    if setting_singleton is None:
        setting_singleton = Settings()
    return setting_singleton

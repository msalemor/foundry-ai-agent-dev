from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from settings import get_settings
from logger import get_logger

logger = get_logger(__name__)

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

settings = get_settings()
client = None
if settings.key:
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.endpoint,
        api_key=settings.key,
        api_version=settings.version,
    )
else:
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.endpoint,
        azure_ad_token_provider=token_provider,
        api_version=settings.version,
    )


async def get_chat_completion(messages: list) -> str:
    try:
        if messages:
            logger.info(f"Processing chat completion")
            response = await client.chat.completions.create(
                model=settings.model,  # or your deployed model name
                messages=messages,
                temperature=0.1,
            )
            return response.choices[0].message.content
        return ""
    except Exception as e:
        return f"Error: {str(e)}"


async def get_embeddings(text: str) -> list[float]:
    try:
        if text:
            logger.info(
                f"Generating embeddings for text: {text[:50]}..."
            )  # Log first 50 chars
            response = await client.embeddings.create(
                model="text-embedding-ada-002",  # or your deployed embedding model
                input=text,
            )
            return response.data[0].embedding
        return []
    except Exception as e:
        return f"Error: {str(e)}"

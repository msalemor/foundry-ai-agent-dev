from services.openai_service import get_embeddings
from services.logger_service import get_logger

logger = get_logger(__name__)


def read_file():
    logger.info("Reading file content...")
    # Read file as text
    file_path = "demos/data/faq.md"  # Replace with your file path

    file_content = None
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    if not file_content:
        print("File is empty or not found.")
        return
    return file_content


async def poor_mans_vectordb():
    """Create a simple vector database from the file content."""
    # logger.info("Creating vector database from file content...")
    logger.info(f"Creating a simple vector database from the file content...")
    paragraphs = read_file().split("\n\n")
    poor_man_vectordb = [
        {"chunk": p, "emb": await get_embeddings(p)} for p in paragraphs
    ]
    return poor_man_vectordb


def _consine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    # logger.info("Calculating cosine similarity...")
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be of the same length")
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = sum(a**2 for a in vec1) ** 0.5
    norm_b = sum(b**2 for b in vec2) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


async def search_vectordb(
    query: str, vectordb: list, relevance: float = 0.5, limit: int = 2
) -> list:
    """Search the vector database for the most similar chunks to the query."""
    logger.info("Searching vector database for relevant chunks...")
    query_embedding = await get_embeddings(query)
    results = []
    for item in vectordb:
        similarity = _consine_similarity(query_embedding, item["emb"])
        if similarity >= relevance:
            results.append((item["chunk"], similarity))

    # Sort by similarity score in descending order
    if len(results) == 0:
        return []
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]  # Return top 5 results

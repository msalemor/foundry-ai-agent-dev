# TBD
import click
from vectordb import poor_mans_vectordb, search_vectordb
from services.openai_service import get_chat_completion, manage_conversation
from services.logger_service import get_logger

logger = get_logger(__name__)


async def main():

    vectordb = await poor_mans_vectordb()
    # NOTE: I could recall the conversation state from a file or database
    conversation = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use the provided context to answer user queries.",
        }
    ]
    while True:
        prompt = input("Enter your prompt [exit or quit]: ")
        if prompt.lower() in ["exit", "quit"]:
            # NOTE: I could serialize and save the conversation state to a file or database
            break

        results = await search_vectordb(prompt, vectordb)

        context = ""
        if results:
            context = "\n".join(chunk for chunk, _ in results)
            logger.info(f"RAG content snippet: {context[:80]}...")  # Log first 80 chars

        # Create and add a user message to the conversation
        message = {"role": "user", "content": prompt + "\n\n" + context}
        conversation.append(message)
        click.echo(click.style(f"User: {prompt}", fg="cyan"))

        # process the completion
        res = await get_chat_completion(messages=manage_conversation(conversation))

        # Add the completion content to the conversation
        conversation.append({"role": "assistant", "content": res})
        click.echo(click.style(f"Assistant: {res}", fg="green"))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

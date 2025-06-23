# TBD
import click
from services.vectordb_service import poor_mans_vectordb, search_vectordb
from services.openai_service import get_chat_completion, manage_conversation
from services.logger_service import get_logger

logger = get_logger(__name__)

conversations = {}
vectordb = None


async def process(userid, prompt):
    # See if the conversation exists for the user
    if userid not in conversations:
        conversations[userid] = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use the provided context to answer user queries.",
            }
        ]
    conversation = conversations[userid]
    results = await search_vectordb(prompt, vectordb)

    context = ""
    if results:
        context = "\n".join(chunk for chunk, _ in results)
        logger.info(f"RAG content snippet: {context[:80]}...")  # Log first 80 chars

    # Create and add a user message to the conversation
    message = {"role": "user", "content": prompt + "\n\n" + context}
    conversation.append(message)
    click.echo(click.style(f"{userid}: {prompt}", fg="cyan"))

    # process the completion
    res = await get_chat_completion(messages=manage_conversation(conversation))

    # Add the completion content to the conversation
    conversation.append({"role": "assistant", "content": res})
    click.echo(click.style(f"Assistant: {res}", fg="green"))


async def main():
    global vectordb

    vectordb = await poor_mans_vectordb()
    await process("user1", "List three restaurants in London?")
    await process("user1", "List three more")
    await process("user1", "What time is it?")
    await process("user2", "Summarize the company values?")
    await process(
        "user2", "Create a document 'values.docx' with the summary of company values."
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

# TBD
import click
from vectordb import get_vectordb, search_vectordb
from openaitools import get_chat_completion
from logger import get_logger

logger = get_logger(__name__)


def manage_conversation(conversation):
    """Manage the conversation history."""
    # always keep the system message as the first message and the last five messages
    logger.info(f"Managing conversation history, current length: {len(conversation)}")

    if len(conversation) > 5:
        conversation = conversation[:1] + conversation[-4:]
    return conversation


async def main():

    vectordb = await get_vectordb()
    conversation = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use the provided context to answer user queries.",
        }
    ]
    while True:
        prompt = input("Enter your prompt [exit or quit]: ")
        if prompt.lower() in ["exit", "quit"]:
            break

        results = await search_vectordb(prompt, vectordb)
        context = ""

        if results:
            context = "\n".join(chunk for chunk, _ in results)

        message = {"role": "user", "content": prompt + "\n\n" + context}
        conversation.append(message)
        # print("User:", prompt)
        click.echo(click.style(f"User: {prompt}", fg="cyan"))

        res = await get_chat_completion(messages=manage_conversation(conversation))

        conversation.append({"role": "assistant", "content": res})
        click.echo(click.style(f"Assistant: {res}", fg="green"))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

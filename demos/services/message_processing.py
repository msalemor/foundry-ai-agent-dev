from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    OpenAIPageableListOfThreadMessage,
    ThreadMessage,
    MessageContent,
    MessageTextContent,
)


def process_last_message(
    client: AIProjectClient,
    messages: OpenAIPageableListOfThreadMessage,
) -> str:
    """
    Process a list of messages and return their responses.
    """
    text_messages: list[MessageTextContent] = messages.text_messages
    data: list[ThreadMessage] = messages.data
    message: ThreadMessage = data[0] if data else None
    content: list[MessageContent] = message.content if message else None
    response = ""
    for content_item in content:
        match content_item.type:
            case "text":
                response += f"{content_item.text.value}\n"
            case "image_file":
                id = content_item.image_file.file_id
                response += f"Generated File ID: {id}.png\n"
                client.agents.save_file(file_id=id, file_name=f"{id}.png")
                response += f"File saved as {id}.png\n"
            case _:
                return f"{str(content_item)}\n"
    return response

import json
from services.logger_service import get_logger

logger = get_logger(__name__)


def mock_send_email(recipient: str, subject: str, body: str) -> str:
    """
    Mock function to simulate sending an email.

    :param recipient: The email address of the recipient.
    :param subject: The subject of the email.
    :param body: The body content of the email.
    :return: Confirmation message as a JSON string.
    """
    logger.info(
        f"Sending email to {recipient} with subject '{subject}' and body '{body}'"
    )
    return json.dumps(
        {
            "status": "success",
            "message": f"Email sent to {recipient} with subject '{subject}'.",
        }
    )


if __name__ == "__main__":
    # Example usage
    recipient = ""
    subject = "Test Email"
    body = "This is a test email body."
    result = mock_send_email(recipient, subject, body)
    print(result)

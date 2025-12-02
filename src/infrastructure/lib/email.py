import asyncio
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiosmtplib
from decouple import config

from src.infrastructure.lib.logger import guide_logger


class EmailSender:
    """A utility class for sending emails through Gmail SMTP server."""

    _sender_email = None
    _sender_password = None
    _smtp_server = "smtp.gmail.com"
    _smtp_port = 587
    _logger = guide_logger

    @classmethod
    def _get_credentials(cls):
        """Get credentials from environment variables."""
        if cls._sender_email is None or cls._sender_password is None:
            cls._sender_email = config("EMAIL_SENDER_EMAIL")
            cls._sender_password = config("EMAIL_SENDER_PASSWORD")

            if not cls._sender_email or not cls._sender_password:
                raise ValueError(
                    "EMAIL_SENDER_EMAIL and EMAIL_SENDER_PASSWORD environment variables must be set"
                )

        return cls._sender_email, cls._sender_password

    @classmethod
    async def _create_connection(cls) -> aiosmtplib.SMTP:
        """Create and return an authenticated SMTP connection."""
        try:
            sender_email, sender_password = cls._get_credentials()
            server = aiosmtplib.SMTP(hostname=cls._smtp_server, port=cls._smtp_port)
            await server.connect()

            await server.login(sender_email, sender_password)
            return server
        except Exception as e:
            cls._logger.error(f"Failed to create SMTP connection: {e}")
            raise

    @classmethod
    async def send_simple_email(
        cls,
        to_email: Union[str, List[str]],
        subject: str,
        body: str,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
    ) -> bool:
        """
        Send a simple text email.

        Args:
            to_email: Recipient email(s)
            subject: Email subject
            body: Email body text
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            sender_email, _ = cls._get_credentials()
            msg = MIMEText(body)
            msg["From"] = sender_email
            msg["Subject"] = subject

            recipients = cls._prepare_recipients(to_email, cc, bcc)
            msg["To"] = (
                ", ".join(recipients["to"])
                if isinstance(recipients["to"], list)
                else recipients["to"]
            )

            if recipients["cc"]:
                msg["Cc"] = (
                    ", ".join(recipients["cc"])
                    if isinstance(recipients["cc"], list)
                    else recipients["cc"]
                )

            server = await cls._create_connection()
            try:
                all_recipients = (
                    recipients["to"]
                    + (recipients["cc"] or [])
                    + (recipients["bcc"] or [])
                )
                await server.send_message(msg, recipients=all_recipients)
            finally:
                await server.quit()

            cls._logger.info(f"Simple email sent successfully to {recipients['to']}")
            return True

        except Exception as e:
            cls._logger.error(f"Failed to send simple email: {e}")
            return False

    @classmethod
    async def send_html_email(
        cls,
        to_email: Union[str, List[str]],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
    ) -> bool:
        """
        Send an HTML email with optional text fallback.

        Args:
            to_email: Recipient email(s)
            subject: Email subject
            html_body: HTML content
            text_body: Plain text fallback (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            sender_email, _ = cls._get_credentials()
            msg = MIMEMultipart("alternative")
            msg["From"] = sender_email
            msg["Subject"] = subject

            recipients = cls._prepare_recipients(to_email, cc, bcc)
            msg["To"] = (
                ", ".join(recipients["to"])
                if isinstance(recipients["to"], list)
                else recipients["to"]
            )

            if recipients["cc"]:
                msg["Cc"] = (
                    ", ".join(recipients["cc"])
                    if isinstance(recipients["cc"], list)
                    else recipients["cc"]
                )

            if text_body:
                text_part = MIMEText(text_body, "plain")
                msg.attach(text_part)

            html_part = MIMEText(html_body, "html")
            msg.attach(html_part)

            server = await cls._create_connection()
            try:
                all_recipients = (
                    recipients["to"]
                    + (recipients["cc"] or [])
                    + (recipients["bcc"] or [])
                )
                await server.send_message(msg, recipients=all_recipients)
            finally:
                await server.quit()

            cls._logger.info(f"HTML email sent successfully to {recipients['to']}")
            return True

        except Exception as e:
            cls._logger.error(f"Failed to send HTML email: {e}")
            return False

    @classmethod
    async def send_email_with_attachments(
        cls,
        to_email: Union[str, List[str]],
        subject: str,
        body: str,
        attachments: List[Union[str, Path, Dict[str, Any]]],
        is_html: bool = False,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
    ) -> bool:
        """
        Send an email with attachments.

        Args:
            to_email: Recipient email(s)
            subject: Email subject
            body: Email body
            attachments: List of file paths, Path objects, or dicts with 'data' (bytes), 'filename' (str), and optional 'mime_type' (str)
            is_html: Whether body is HTML
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            sender_email, _ = cls._get_credentials()
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["Subject"] = subject

            recipients = cls._prepare_recipients(to_email, cc, bcc)
            msg["To"] = (
                ", ".join(recipients["to"])
                if isinstance(recipients["to"], list)
                else recipients["to"]
            )

            if recipients["cc"]:
                msg["Cc"] = (
                    ", ".join(recipients["cc"])
                    if isinstance(recipients["cc"], list)
                    else recipients["cc"]
                )

            body_type = "html" if is_html else "plain"
            msg.attach(MIMEText(body, body_type))

            for attachment in attachments:
                if await cls._add_attachment(msg, attachment):
                    attachment_name = (
                        attachment
                        if isinstance(attachment, (str, Path))
                        else attachment.get("filename", "attachment")
                    )
                    cls._logger.info(f"Added attachment: {attachment_name}")
                else:
                    attachment_name = (
                        attachment
                        if isinstance(attachment, (str, Path))
                        else attachment.get("filename", "attachment")
                    )
                    cls._logger.warning(f"Failed to add attachment: {attachment_name}")

            server = await cls._create_connection()
            try:
                all_recipients = (
                    recipients["to"]
                    + (recipients["cc"] or [])
                    + (recipients["bcc"] or [])
                )
                await server.send_message(msg, recipients=all_recipients)
            finally:
                await server.quit()

            cls._logger.info(
                f"Email with attachments sent successfully to {recipients['to']}"
            )
            return True

        except Exception as e:
            cls._logger.error(f"Failed to send email with attachments: {e}")
            return False

    @classmethod
    def _prepare_recipients(cls, to_email, cc=None, bcc=None) -> dict:
        """Prepare and validate recipient lists."""

        def ensure_list(emails):
            if emails is None:
                return []
            if isinstance(emails, str):
                return [emails]
            return list(emails)

        return {
            "to": ensure_list(to_email),
            "cc": ensure_list(cc) if cc else [],
            "bcc": ensure_list(bcc) if bcc else [],
        }

    @classmethod
    async def _add_attachment(
        cls, msg: MIMEMultipart, attachment: Union[str, Path, Dict[str, Any]]
    ) -> bool:
        """Add a file attachment to the message from file path or bytes data."""
        try:
            if isinstance(attachment, dict):
                if "data" not in attachment or "filename" not in attachment:
                    cls._logger.error(
                        "Attachment dict must contain 'data' and 'filename' keys"
                    )
                    return False

                file_content = attachment["data"]
                filename = attachment["filename"]
                mime_type = attachment.get("mime_type", "application/octet-stream")

                if not isinstance(file_content, bytes):
                    cls._logger.error(
                        f"Attachment data must be bytes, got {type(file_content)}"
                    )
                    return False

                part = MIMEBase("application", "octet-stream")
                if mime_type != "application/octet-stream":
                    main_type, sub_type = mime_type.split("/", 1)
                    part = MIMEBase(main_type, sub_type)

                part.set_payload(file_content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition", f"attachment; filename= {filename}"
                )
                msg.attach(part)
                return True

            else:
                file_path = Path(attachment)

                if not file_path.exists():
                    cls._logger.error(f"Attachment file not found: {file_path}")
                    return False

                loop = asyncio.get_event_loop()

                def read_file():
                    with open(file_path, "rb") as attachment_file:
                        return attachment_file.read()

                file_content = await loop.run_in_executor(None, read_file)

                part = MIMEBase("application", "octet-stream")
                part.set_payload(file_content)

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition", f"attachment; filename= {file_path.name}"
                )

                msg.attach(part)
                return True

        except Exception as e:
            cls._logger.error(f"Failed to add attachment {attachment}: {e}")
            return False

    @classmethod
    async def test_connection(cls) -> bool:
        """Test the SMTP connection and credentials."""
        try:
            server = await cls._create_connection()
            await server.quit()
            cls._logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            cls._logger.error(f"SMTP connection test failed: {e}")
            return False

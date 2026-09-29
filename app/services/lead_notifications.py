import logging
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_lead_notification(
	*,
	name: str,
	email: str,
	phone: str | None,
	source: str,
	budget: str | None,
	requirement: str | None,
) -> None:
	"""Send the business inbox an email about a newly created lead."""
	host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
	username = os.getenv("SMTP_USERNAME", "kelebekdesigners@gmail.com").strip()
	password = os.getenv("SMTP_PASSWORD", "zkvs wphh wyoe rkog")
	recipient = os.getenv("LEAD_NOTIFICATION_EMAIL", "kelebekdesigners@gmail.com").strip()

	if not all((host, username, password, recipient)):
		logger.warning(
			"Lead notification not sent: configure SMTP_USERNAME, SMTP_PASSWORD, "
			"and LEAD_NOTIFICATION_EMAIL in the backend environment."
		)
		return

	message = EmailMessage()
	message["Subject"] = "New lead received"
	message["From"] = os.getenv("SMTP_FROM_EMAIL", "kelebekdesigners@gmail.com").strip() or username
	message["To"] = recipient
	message.set_content(
		"A new lead was submitted.\n\n"
		f"Name: {name}\n"
		f"Lead email: {email}\n"
		f"Phone: {phone or 'Not provided'}\n"
		f"Source: {source}\n"
		f"Budget: {budget or 'Not provided'}\n"
		f"Requirement: {requirement or 'Not provided'}\n"
	)

	try:
		port = int(os.getenv("SMTP_PORT", "587"))
		timeout = float(os.getenv("SMTP_TIMEOUT", "15"))
		if port == 465:
			with smtplib.SMTP_SSL(host, port, timeout=timeout) as server:
				server.login(username, password)
				server.send_message(message)
		else:
			with smtplib.SMTP(host, port, timeout=timeout) as server:
				server.ehlo()
				server.starttls()
				server.ehlo()
				server.login(username, password)
				server.send_message(message)
		logger.info("New-lead notification email sent to %s.", recipient)
	except Exception:
		# A mail provider outage must not undo an already-saved lead.
		logger.exception("Failed to send a new-lead notification email.")

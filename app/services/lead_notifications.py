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
) -> dict[str, str | bool | None]:
	"""Send a new-lead email and return its actual delivery result."""
	host = "smtp.gmail.com"
	username = "kelebekdesigners@gmail.com"
	password = "zkvs wphh wyoe rkog"
	recipient = "kelebekdesigners@gmail.com"

	if not all((host, username, password, recipient)):
		error = "SMTP host, username, password, or recipient is not configured."
		logger.warning(
			"Lead notification not sent: %s",
			error,
		)
		return {"sent": False, "error": error}

	message = EmailMessage()
	message["Subject"] = "New lead received"
	message["From"] = "kelebekdesigners@gmail.com"
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
		port = int("587")
		timeout = float("15")
		if port == 465:
			with smtplib.SMTP_SSL(host, port, timeout=timeout) as server:
				server.login(username, password)
				refused = server.send_message(message)
		else:
			with smtplib.SMTP(host, port, timeout=timeout) as server:
				server.ehlo()
				server.starttls()
				server.ehlo()
				server.login(username, password)
				refused = server.send_message(message)
		if refused:
			rejected = ", ".join(
				f"{address} (SMTP {reply[0]})"
				for address, reply in refused.items()
			)
			error = f"SMTP rejected recipient: {rejected}"
			logger.error(error)
			return {"sent": False, "error": error}
		logger.info("New-lead notification email sent to %s.", recipient)
		return {"sent": True, "error": None}
	except smtplib.SMTPAuthenticationError:
		error = "SMTP authentication failed. Check the Gmail address and current Google App Password."
		logger.exception(error)
		return {"sent": False, "error": error}
	except Exception as exc:
		# A mail provider outage must not undo an already-saved lead.
		logger.exception("Failed to send a new-lead notification email.")
		return {"sent": False, "error": f"{type(exc).__name__}: {exc}"}

import logging
import smtplib
from email.message import EmailMessage
import os

EMAIL_HOST = os.getenv("zoho_smtp_host")
EMAIL_PORT = int(os.getenv("zoho_smtp_port", 587))
EMAIL_HOST_USER = os.getenv("zoho_smtp_user")
EMAIL_HOST_PASSWORD = os.getenv("zoho_smtp_password")

logger = logging.getLogger(__name__)

# Zoho Mail SMTP settings. Replace the password with a newly generated
# Zoho app-specific password after revoking the one previously used here.
SMTP_HOST = EMAIL_HOST
SMTP_PORT = EMAIL_PORT
SMTP_USERNAME = EMAIL_PORT
SMTP_PASSWORD = EMAIL_PORT
SMTP_FROM = EMAIL_HOST
SMTP_TO = SMTP_USERNAME


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
	if not SMTP_PASSWORD or SMTP_PASSWORD == "REPLACE_WITH_NEW_ZOHO_APP_PASSWORD":
		error = "Set SMTP_PASSWORD to a newly generated Zoho app-specific password."
		logger.warning(
			"Lead notification not sent: %s",
			error,
		)
		return {"sent": False, "error": error}

	message = EmailMessage()
	message["Subject"] = "New lead received"
	message["From"] = SMTP_FROM
	message["To"] = SMTP_TO
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
		timeout = 15.0
		if SMTP_PORT == 465:
			with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=timeout) as server:
				server.login(SMTP_USERNAME, SMTP_PASSWORD)
				refused = server.send_message(message)
		else:
			with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=timeout) as server:
				server.ehlo()
				server.starttls()
				server.ehlo()
				server.login(SMTP_USERNAME, SMTP_PASSWORD)
				refused = server.send_message(message)
		if refused:
			rejected = ", ".join(
				f"{address} (SMTP {reply[0]})"
				for address, reply in refused.items()
			)
			error = f"SMTP rejected recipient: {rejected}"
			logger.error(error)
			return {"sent": False, "error": error}
		logger.info("New-lead notification email sent to %s.", SMTP_TO)
		return {"sent": True, "error": None}
	except smtplib.SMTPAuthenticationError as exc:
		reply = exc.smtp_error.decode(errors="replace") if isinstance(exc.smtp_error, bytes) else str(exc.smtp_error)
		error = f"SMTP authentication failed (code {exc.smtp_code}): {reply}"
		logger.exception(error)
		return {"sent": False, "error": error}
	except smtplib.SMTPRecipientsRefused as exc:
		error = f"SMTP rejected recipient: {exc.recipients}"
		logger.exception(error)
		return {"sent": False, "error": error}
	except Exception as exc:
		# A mail provider outage must not undo an already-saved lead.
		logger.exception("Failed to send a new-lead notification email.")
		return {"sent": False, "error": f"{type(exc).__name__}: {exc}"}

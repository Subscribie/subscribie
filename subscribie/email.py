import logging
from email.message import EmailMessage
from flask import current_app, session, request, render_template
import flask
from subscribie.models import (
    Setting,
    User,
    Company,
    Plan,
    EmailTemplate,
)
from pathlib import Path
from jinja2 import Template
import time
import os

log = logging.getLogger(__name__)


class EmailMessageQueue(EmailMessage):
    def queue(self):
        fileName = time.time_ns()
        try:
            email_queue_folder = os.environ.get("EMAIL_QUEUE_FOLDER")
            with open(f"{email_queue_folder}/{fileName}", "wb") as f:
                f.write(self.as_bytes())
                log.debug(f"Written email to queue folder {email_queue_folder}")
        except Exception as e:
            log.error(
                f"Error when writing EmailMessageQueue folder: {email_queue_folder}. {e}"  # noqa
            )


def send_welcome_email():
    company = Company.query.first()
    plan = Plan.query.filter_by(uuid=session.get("plan", None)).first()

    # Send welcome email (either default template of custom, if active)
    custom_template = EmailTemplate.query.first()
    if custom_template is not None and custom_template.use_custom_welcome_email is True:
        # Load custom welcome email
        template = custom_template.custom_welcome_email_template
    else:
        # Load default welcome email from template folder
        welcome_template = str(
            Path(current_app.root_path + "/emails/welcome.jinja2.html")
        )
        fp = open(welcome_template)
        template = fp.read()
        fp.close()
    first_charge_date = session.get("first_charge_date", None)
    first_charge_amount = session.get("first_charge_amount", None)
    jinja_template = Template(template)
    scheme = "https://" if request.is_secure else "http://"
    html = jinja_template.render(
        first_name=session.get("given_name", None),
        company_name=company.name,
        subscriber_login_url=scheme + flask.request.host + "/account/login",
        first_charge_date=first_charge_date,
        first_charge_amount=first_charge_amount,
        plan=plan,
        subscriber_email=session.get("email"),
    )

    try:
        msg = EmailMessageQueue()
        msg["Subject"] = company.name + " " + "Subscription Confirmation"
        msg["From"] = current_app.config["EMAIL_LOGIN_FROM"]
        msg["To"] = session["email"]
        msg.set_content("Subscription confirmation")
        msg.add_alternative(html, subtype="html")
        setting = Setting.query.first()
        if setting is not None:
            msg["Reply-To"] = setting.reply_to_email_address
        else:
            msg[
                "Reply-To"
            ] = User.query.first().email  # Fallback to first shop admin email
        msg.queue()
    except Exception as e:
        log.error(f"Failed to send welcome email. {e}")
    finally:
        return render_template("thankyou.html")

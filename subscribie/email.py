import logging
from flask_mail import Mail, Message
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
from threading import Thread

log = logging.getLogger(__name__)


def send_async_email(msg):
    try:
        from subscribie import create_app
    except Exception:
        pass

    app = create_app()
    with app.app_context():
        mail = Mail(app)
        log.info("Sending async email")
        mail.send(msg)


def send_welcome_email():
    Mail(current_app)
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
        msg = Message()
        msg.subject = company.name + " " + "Subscription Confirmation"
        msg.sender = current_app.config["EMAIL_LOGIN_FROM"]
        msg.recipients = [session["email"]]
        setting = Setting.query.first()
        if setting is not None:
            msg.reply_to = setting.reply_to_email_address
        else:
            msg.reply_to = (
                User.query.first().email
            )  # Fallback to first shop admin email
        msg.html = html
        Thread(target=send_async_email, args=(msg,)).start()
    except Exception as e:
        log.warning(f"Failed to send welcome email. {e}")
    finally:
        return render_template("thankyou.html")

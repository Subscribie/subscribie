import functools
import binascii
import os
from pathlib import Path
import flask
from flask import (
    Blueprint, render_template, flash, redirect, url_for,
    session, g, current_app, request
)
from subscribie import PasswordLoginForm, SubscriberForgotPasswordForm, SubscriberResetPasswordForm
from subscribie.models import Subscription, database, Person, Company, Option, ChosenOption
from flask_mail import Mail, Message
from jinja2 import Template

subscriber = Blueprint("subscriber", __name__, template_folder="templates", url_prefix=None)

@subscriber.before_app_request
def load_logged_in_subscriber():
    subscriber_id = session.get("subscriber_id")

    if subscriber_id is None:
        g.subscriber = None
    else:
        g.subscriber = Person.query.filter_by(email=subscriber_id).first()

def subscriber_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.subscriber is None:
            return redirect(url_for("subscriber.login"))

        return view(**kwargs)

    return wrapped_view

def check_password_login(email, password):
    subscriber = Person.query.filter_by(email=email).first()
    if subscriber.check_password(password):
        return True
    return False


@subscriber.route("/account/login", methods=["GET", "POST"])
def login():
    form = PasswordLoginForm()
    if form.validate_on_submit():
        email = form.data['email']
        password = form.data['password']
        subscriber = Person.query.filter_by(email=email).first()
        if subscriber is None:
            flash("Person not found with that email")
            return redirect(url_for("subscriber.login"))

        if check_password_login(email, password):
            session.clear()
            session["subscriber_id"] = subscriber.email
            return redirect(url_for("subscriber.account"))
        else:
            session.clear()
            flash("Invalid password")
            return redirect(url_for("subscriber.login"))
    return render_template('subscriber/login.html', form=form)


@subscriber.route("/account/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = SubscriberForgotPasswordForm()
    if form.validate_on_submit():
        email = form.data['email']
        subscriber = Person.query.filter_by(email=email).first()
        if subscriber is None:
            flash("Person not found with that email")
            return redirect(url_for("subscriber.forgot_password"))
        # Generate password reset token
        token = binascii.hexlify(os.urandom(32)).decode()
        subscriber.password_reset_string = token
        database.session.commit()

        email_template = str(Path(current_app.root_path + '/emails/subscriber-reset-password.jinja2.html'))
        company = Company.query.first()
        password_reset_url='https://' + flask.request.host + '/account/password-reset?token=' + token

        with open(email_template) as file_:                                   
            template = Template(file_.read())     
            html = template.render(password_reset_url=password_reset_url,
                                    company=company) 

            try:
                mail = Mail(current_app)
                msg = Message()
                msg.subject = company.name + " " + "Password Reset"
                msg.sender = current_app.config["EMAIL_LOGIN_FROM"]
                msg.recipients = [email]
                msg.html = html
                mail.send(msg)
            except Exception as e:
                print(e)
                print("Failed to send subscriber password reset email")
            flash("We've sent you an email with a password reset link, please check your spam/junk folder too")

    return render_template('subscriber/forgot_password.html', form=form)

@subscriber.route("/account/password-reset", methods=["GET", "POST"])
def password_reset():
    "Perform password reset from email link, verify token"
    form = SubscriberResetPasswordForm()

    if form.validate_on_submit():
        if Person.query.filter_by(password_reset_string=form.data['token']).first() == None:
            return "Invalid reset token"
        
        person = Person.query.filter_by(password_reset_string=form.data['token']).first()
        person.set_password(form.data['password'])
        database.session.commit()
        flash("Your password has been reset")
        return redirect(url_for('subscriber.login'))

    if request.args.get("token", None) is None or \
       len(request.args["token"]) != 64 or \
       Person.query.filter_by(password_reset_string=request.args["token"]).first() == None:
       return "Invalid reset link. Please try generating a new reset link."

    return render_template('subscriber/reset_password.html',
                        token=request.args["token"],
                        form=form)


@subscriber.route("/account")
@subscriber_login_required
def account():
    "A subscribers account home screen"
    return render_template('subscriber/account.html')

@subscriber.route('/account/subscriptions')
@subscriber_login_required
def subscriptions():
    "A subscribers subscriptions"
    return render_template('subscriber/subscriptions.html')

@subscriber.route('/account/subscriptions/update-choices/<subscription_id>', methods=["GET", "POST"])
@subscriber_login_required
def update_subscription_choices(subscription_id):
    """Subscriber can update their subscription choices"""
    # Get plan from subscription
    subscription = Subscription.query.get(subscription_id)
    plan = subscription.plan
    if request.method == "POST":
        chosen_option_ids = []
        for choice_group_id in request.form.keys():
            for option_id in request.form.getlist(choice_group_id):
                chosen_option_ids.append(option_id)
        # Update chosen choices
        chosen_options = []
        for option_id in chosen_option_ids:
            option = Option.query.get(option_id)
            # We will store as ChosenOption because option may change after the order has processed
            # This preserves integrity of the actual chosen options
            chosen_option = ChosenOption()
            chosen_option.option_title = option.title
            chosen_option.choice_group_title = option.choice_group.title
            chosen_option.choice_group_id = option.choice_group.id # Used for grouping latest choice
            chosen_options.append(chosen_option)
        subscription.chosen_options = chosen_options

        database.session.add(subscription)
        database.session.commit()
        flash("Your choices have been saved.")
        return redirect(url_for('subscriber.subscriptions'))
    else:
        return render_template('subscriber/update_choices.html', plan=plan)
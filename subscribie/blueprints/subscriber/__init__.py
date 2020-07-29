import functools
from flask import (
    Blueprint, render_template, flash, redirect, url_for,
    session, g
)
from subscribie import PasswordLoginForm
from subscribie.models import Person

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

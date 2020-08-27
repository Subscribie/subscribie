from . import admin
from subscribie.auth import login_required
from subscribie.models import Person
from flask import render_template

@admin.route("/show-subscriber/<subscriber_id>", methods=["GET", "POST"])
@login_required
def show_subscriber(subscriber_id):
    person = Person.query.get(subscriber_id)
    return render_template("admin/subscriber/show_subscriber.html", 
                            person=person)

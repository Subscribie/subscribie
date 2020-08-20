from subscribie.blueprints.admin import choice_group
from . import admin
from subscribie import database
from subscribie.auth import login_required
from subscribie.forms import OptionForm
from subscribie.models import ChoiceGroup, Option
from flask import (request, render_template, url_for, flash, redirect
)

@admin.route("/add-option/choice_group_id/<choice_group_id>", methods=["GET", "POST"])
@login_required
def add_option(choice_group_id):
    form = OptionForm()
    choice_group = ChoiceGroup.query.get(choice_group_id)
    if form.validate_on_submit():
        option = Option()
        option.title = request.form['title']
        choice_group.options.append(option)
        database.session.commit()
        flash("Added new option")
        return redirect(url_for('admin.list_options', choice_group_id=choice_group_id))
    
    return render_template("admin/option/add_option.html", form=form)

@admin.route("/list-options/<choice_group_id>", methods=["GET", "POST"])
@login_required
def list_options(choice_group_id):
    choice_group = ChoiceGroup.query.get(choice_group_id)
    return render_template("admin/option/list_options.html", 
                            choice_group=choice_group)

@admin.route("/edit-option/<id>", methods=["GET", "POST"])
@login_required
def edit_option(id):
    option = Option.query.get(id)
    if request.method == 'POST':
        option.title = request.form['title']
        database.session.commit()
        flash("Choice option updated")
    return render_template("admin/option/edit_option.html", option=option)

@admin.route("/delete-option/<option_id>/choice_group_id/<choice_group_id>", methods=["GET"])
@login_required
def delete_option(option_id,choice_group_id):
    choice_group = ChoiceGroup.query.get(choice_group_id)
    if "confirm" in request.args:
        options = Option.query.all()

        return render_template(
            "admin/option/list_options.html",
            options=options,
            option=Option.query.get(option_id),
            choice_group=choice_group,
            confirm=False,
        )
    option = Option.query.get(option_id)
    database.session.delete(option)
    database.session.commit()
    flash("Choice option deleted")
    return redirect(url_for('admin.list_options', choice_group_id=choice_group.id))
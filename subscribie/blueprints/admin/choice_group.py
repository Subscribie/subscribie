from . import admin
from subscribie import database
from subscribie.auth import login_required
from subscribie.forms import ChoiceGroupForm
from subscribie.models import ChoiceGroup, Plan
from flask import (request, render_template, url_for, flash, redirect
)

@admin.route("/add-choice-group", methods=["GET", "POST"])
@login_required
def add_choice_group():
    form = ChoiceGroupForm()
    if form.validate_on_submit():
        choice_group = ChoiceGroup()
        choice_group.title = request.form['title']
        choice_group.description = request.form['description']
        database.session.add(choice_group)
        database.session.commit()
        flash("Added new choice group")
        return redirect(url_for('admin.list_choice_groups'))
    
    return render_template("admin/choice_group/add_choice_group.html", form=form)

@admin.route("/list-choice-groups", methods=["GET", "POST"])
@login_required
def list_choice_groups():
    choice_groups = ChoiceGroup.query.all()
    return render_template("admin/choice_group/list_choice_groups.html", choice_groups=choice_groups)

@admin.route("/edit-choice-group/<id>", methods=["GET", "POST"])
@login_required
def edit_choice_group(id):
    choice_group = ChoiceGroup.query.get(id)
    if request.method == 'POST':
        choice_group.title = request.form['title']
        choice_group.description = request.form['description']
        database.session.commit()
        flash("Choice group updated")
    return render_template("admin/choice_group/edit_choice_group.html", choice_group=choice_group)

@admin.route("/choice-group/<choice_group_id>/assign-plan", methods=["GET", "POST"])
@login_required
def choice_group_assign_plan(choice_group_id):
    choice_group = ChoiceGroup.query.get(choice_group_id)
    plans = Plan.query.filter_by(archived=0)

    if request.method == "POST":
        # Remove choice group if not selected
        for plan in plans:
            if choice_group in plan.choice_groups:
                plan.choice_groups.remove(choice_group)

        for plan_id in request.form.getlist("assign"):
            plan = Plan.query.get(plan_id)
            plan.choice_groups.append(choice_group)
        
        database.session.commit()
        flash("Choice group has been added to selected plan(s)")
        return redirect(url_for('admin.list_choice_groups'))
        
        

    return render_template("admin/choice_group/choice_group_assign_plan.html",
                            choice_group=choice_group,
                            plans=plans)


@admin.route("/delete-choice-group/<id>", methods=["GET"])
@login_required
def delete_choice_group(id):
    if "confirm" in request.args:
        choice_groups = ChoiceGroup.query.all()

        confirm = False
        return render_template(
            "admin/choice_group/list_choice_groups.html",
            choice_groups=choice_groups,
            choice_group=ChoiceGroup.query.get(id),
            confirm=False,
        )
    choice_group = ChoiceGroup.query.get(id)
    database.session.delete(choice_group)
    database.session.commit()
    flash("Choice group deleted")
    return redirect(url_for('admin.list_choice_groups'))